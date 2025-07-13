import re
import os
from typing import Any, Dict, List, Optional
from openai import OpenAI
from openai import OpenAIError, APIError, RateLimitError

class OpenAIFunctionParser:
    """Parser for HF() function calls in spreadsheet cells - now using OpenAI"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.hf_function_pattern = r'=HF\(([^,]+),\s*"([^"]+)",\s*"([^"]+)"\)'
    
    def is_hf_function(self, cell_value: str) -> bool:
        """Check if cell contains an HF function"""
        if not isinstance(cell_value, str):
            return False
        return bool(re.match(self.hf_function_pattern, cell_value.strip()))
    
    def parse_hf_function(self, cell_value: str) -> Optional[Dict[str, str]]:
        """Parse HF function and extract parameters"""
        match = re.match(self.hf_function_pattern, cell_value.strip())
        if not match:
            return None
        
        return {
            "text_reference": match.group(1).strip(),
            "model": match.group(2).strip(),  # Will be ignored, using GPT-4o
            "prompt": match.group(3).strip()
        }
    
    def resolve_cell_reference(self, reference: str, sheet_data: List[List[Any]]) -> str:
        """Resolve cell reference (like A1, B2) to actual cell value"""
        # Simple implementation for basic cell references
        # Supports format like A1, B2, etc.
        match = re.match(r'([A-Z]+)(\d+)', reference.strip())
        if not match:
            return reference  # Return as-is if not a cell reference
        
        col_letters = match.group(1)
        row_num = int(match.group(2)) - 1  # Convert to 0-based index
        
        # Convert column letters to index (A=0, B=1, etc.)
        col_num = 0
        for i, letter in enumerate(reversed(col_letters)):
            col_num += (ord(letter) - ord('A') + 1) * (26 ** i)
        col_num -= 1  # Convert to 0-based index
        
        # Get the cell value
        try:
            if 0 <= row_num < len(sheet_data) and 0 <= col_num < len(sheet_data[row_num]):
                cell_value = sheet_data[row_num][col_num]
                return str(cell_value) if cell_value is not None else ""
            else:
                return ""
        except (IndexError, TypeError):
            return ""
    
    async def execute_hf_function(self, cell_value: str, sheet_data: List[List[Any]]) -> str:
        """Execute HF function and return result using OpenAI"""
        parsed = self.parse_hf_function(cell_value)
        if not parsed:
            return "Error: Invalid HF function format"
        
        # Resolve cell reference to get actual text
        text = self.resolve_cell_reference(parsed["text_reference"], sheet_data)
        
        if not text:
            return "Error: Referenced cell is empty"
        
        # Call OpenAI API
        try:
            result = await self.call_openai_api(
                text=text,
                prompt=parsed["prompt"]
            )
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def call_openai_api(self, text: str, prompt: str) -> str:
        """Call OpenAI API using GPT-4o"""
        try:
            # Create the full prompt with context
            full_prompt = f"{prompt}\n\nText to process: {text}"
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that processes data in spreadsheets. Provide concise, accurate responses. Follow the user's instructions exactly."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except RateLimitError:
            return "Error: OpenAI rate limit exceeded"
        except APIError as e:
            return f"Error: OpenAI API error - {str(e)}"
        except OpenAIError as e:
            return f"Error: OpenAI service error - {str(e)}"
        except Exception as e:
            return f"Error: Unexpected error - {str(e)}"

class SheetProcessor:
    """Process entire sheets to execute HF functions using OpenAI"""
    
    def __init__(self, api_key: str):
        self.parser = OpenAIFunctionParser(api_key)
    
    async def process_sheet(self, sheet_data: List[List[Any]]) -> List[List[Any]]:
        """Process entire sheet and execute all HF functions"""
        processed_data = []
        
        for row_idx, row in enumerate(sheet_data):
            processed_row = []
            for col_idx, cell in enumerate(row):
                if self.parser.is_hf_function(cell):
                    # Execute HF function
                    result = await self.parser.execute_hf_function(cell, sheet_data)
                    processed_row.append(result)
                else:
                    # Keep original value
                    processed_row.append(cell)
            processed_data.append(processed_row)
        
        return processed_data
    
    async def process_cell(self, row: int, col: int, sheet_data: List[List[Any]]) -> str:
        """Process a single cell if it contains an HF function"""
        try:
            cell_value = sheet_data[row][col]
            if self.parser.is_hf_function(cell_value):
                return await self.parser.execute_hf_function(cell_value, sheet_data)
            else:
                return str(cell_value)
        except (IndexError, TypeError):
            return ""
