from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import httpx
from dotenv import load_dotenv
from openai_functions import OpenAIFunctionParser, SheetProcessor

load_dotenv()

app = FastAPI(title="AI Sheets API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class HFRequest(BaseModel):
    text: str
    model: str  # Will be ignored, using GPT-4o
    prompt: str
    system_prompt: Optional[str] = "You are a helpful assistant that processes data in spreadsheets. Provide concise, accurate responses."

class CellUpdate(BaseModel):
    row: int
    col: int
    value: str
    formula: Optional[str] = None

class SheetData(BaseModel):
    data: List[List[Any]]

# Store for sheet data (in production, use a database)
sheet_store = {}

async def search_web(query: str, serper_api_key: str) -> str:
    """Search the web using Serper API and return formatted results directly"""
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "q": query,
                "num": 5  # Limit to 5 results
            }
            
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                "https://google.serper.dev/search",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Add knowledge graph if available (most authoritative info)
                if "knowledgeGraph" in data:
                    kg = data["knowledgeGraph"]
                    title = kg.get("title", "")
                    description = kg.get("description", "")
                    if title or description:
                        results.append(f"📊 **{title}**\n{description}")
                
                # Format organic results
                if "organic" in data and len(data["organic"]) > 0:
                    for i, result in enumerate(data["organic"][:3], 1):  # Top 3 results
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")
                        link = result.get("link", "")
                        if title and snippet:
                            results.append(f"🔍 **Result {i}: {title}**\n{snippet}\n📎 {link}")
                
                # Add answer box if available
                if "answerBox" in data:
                    answer = data["answerBox"]
                    answer_text = answer.get("answer", "") or answer.get("snippet", "")
                    if answer_text:
                        results.insert(0 if "knowledgeGraph" not in data else 1, f"💡 **Quick Answer**\n{answer_text}")
                
                # Format for spreadsheet cells - more concise
                if results:
                    # Prioritize answer box or knowledge graph for concise info
                    if "answerBox" in data:
                        answer = data["answerBox"]
                        answer_text = answer.get("answer", "") or answer.get("snippet", "")
                        if answer_text:
                            return answer_text[:500] + "..." if len(answer_text) > 500 else answer_text
                    
                    if "knowledgeGraph" in data:
                        kg = data["knowledgeGraph"]
                        description = kg.get("description", "")
                        if description:
                            return description[:500] + "..." if len(description) > 500 else description
                    
                    # Fall back to first organic result
                    if "organic" in data and len(data["organic"]) > 0:
                        first_result = data["organic"][0]
                        snippet = first_result.get("snippet", "")
                        if snippet:
                            return snippet[:500] + "..." if len(snippet) > 500 else snippet
                    
                    return "Search completed but no suitable summary found."
                else:
                    return "No search results found."
            else:
                return f"Search failed with status: {response.status_code} - {response.text}"
                
    except Exception as e:
        return f"Search error: {str(e)}"

@app.get("/")
async def root():
    return {"message": "AI Sheets API is running"}

@app.options("/hf")
async def hf_options():
    """Handle CORS preflight for /hf endpoint"""
    return {"message": "OK"}

@app.post("/hf")
async def call_openai_model(request: HFRequest, x_api_key: Optional[str] = Header(None), x_serper_key: Optional[str] = Header(None, alias="X-Serper-Key")):
    """Call OpenAI GPT-4o model with text and prompt, with optional web search"""
    # Use API key from header if provided, otherwise fall back to environment variable
    api_key = x_api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not provided in header or environment")
    
    try:
        parser = OpenAIFunctionParser(api_key)
        
        # Check if this is a web search request - be more specific about detection
        prompt_lower = request.prompt.lower()
        is_web_search = (
            "search the web for information about" in prompt_lower or
            "search the web for" in prompt_lower or
            "web search" in prompt_lower or
            "search web" in prompt_lower
        )
        
        if is_web_search:
            serper_key = x_serper_key or os.getenv("SERPER_API_KEY")
            if serper_key:
                print(f"[DEBUG] Performing web search for: {request.text}")
                print(f"[DEBUG] Using Serper API key: {serper_key[:10]}...")
                # Return search results directly without OpenAI processing
                result = await search_web(request.text, serper_key)
                print(f"[DEBUG] Direct search results returned")
            else:
                print("[DEBUG] No Serper API key available - falling back to OpenAI")
                print(f"[DEBUG] Header Serper key: {x_serper_key}")
                print(f"[DEBUG] Env Serper key: {os.getenv('SERPER_API_KEY')}")
                result = await parser.call_openai_api(request.text, request.prompt)
        else:
            result = await parser.call_openai_api(request.text, request.prompt)
        
        return {"result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling OpenAI API: {str(e)}")

@app.get("/models")
async def get_available_models():
    """Get list of available OpenAI models"""
    models = [
        {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "description": "Most capable OpenAI model with vision and advanced reasoning"
        }
    ]
    return {"models": models}

@app.post("/test-search")
async def test_search(query: str, x_serper_key: Optional[str] = Header(None, alias="X-Serper-Key")):
    """Test Serper API integration"""
    serper_key = x_serper_key or os.getenv("SERPER_API_KEY")
    if not serper_key:
        return {"error": "SERPER_API_KEY not provided"}
    
    try:
        results = await search_web(query, serper_key)
        return {"query": query, "results": results}
    except Exception as e:
        return {"error": str(e)}

@app.post("/sheet/{sheet_id}")
async def save_sheet(sheet_id: str, data: SheetData):
    """Save sheet data"""
    sheet_store[sheet_id] = data.data
    return {"message": "Sheet saved successfully"}

@app.get("/sheet/{sheet_id}")
async def get_sheet(sheet_id: str):
    """Get sheet data"""
    if sheet_id not in sheet_store:
        # Return empty 10x10 grid if sheet doesn't exist
        empty_data = [["" for _ in range(10)] for _ in range(10)]
        return {"data": empty_data}
    
    return {"data": sheet_store[sheet_id]}

@app.post("/cell/{sheet_id}")
async def update_cell(sheet_id: str, cell_update: CellUpdate):
    """Update a specific cell"""
    if sheet_id not in sheet_store:
        # Create empty sheet if it doesn't exist
        sheet_store[sheet_id] = [["" for _ in range(10)] for _ in range(10)]
    
    sheet_data = sheet_store[sheet_id]
    
    # Ensure the sheet is large enough
    while len(sheet_data) <= cell_update.row:
        sheet_data.append(["" for _ in range(len(sheet_data[0]) if sheet_data else 10)])
    
    while len(sheet_data[cell_update.row]) <= cell_update.col:
        sheet_data[cell_update.row].append("")
    
    # Update the cell
    sheet_data[cell_update.row][cell_update.col] = cell_update.value
    
    return {"message": "Cell updated successfully"}

@app.post("/process-hf/{sheet_id}")
async def process_hf_functions(sheet_id: str):
    """Process all HF functions in a sheet using OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    if sheet_id not in sheet_store:
        raise HTTPException(status_code=404, detail="Sheet not found")
    
    processor = SheetProcessor(api_key)
    
    try:
        processed_data = await processor.process_sheet(sheet_store[sheet_id])
        sheet_store[sheet_id] = processed_data
        return {"data": processed_data, "message": "HF functions processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing HF functions: {str(e)}")

@app.post("/process-cell/{sheet_id}/{row}/{col}")
async def process_cell_hf_function(sheet_id: str, row: int, col: int):
    """Process HF function in a specific cell using OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")
    
    if sheet_id not in sheet_store:
        raise HTTPException(status_code=404, detail="Sheet not found")
    
    processor = SheetProcessor(api_key)
    
    try:
        result = await processor.process_cell(row, col, sheet_store[sheet_id])
        
        # Update the cell with the result
        if len(sheet_store[sheet_id]) > row and len(sheet_store[sheet_id][row]) > col:
            sheet_store[sheet_id][row][col] = result
        
        return {"result": result, "message": "Cell processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing cell: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)