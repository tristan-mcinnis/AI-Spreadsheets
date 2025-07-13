import re
import requests
import os
from typing import Any, Dict, List, Optional

class HFFunctionParser:
    """Parser for HF() function calls in spreadsheet cells"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
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
            "model": match.group(2).strip(),
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
        """Execute HF function and return result"""
        parsed = self.parse_hf_function(cell_value)
        if not parsed:
            return "Error: Invalid HF function format"
        
        # Resolve cell reference to get actual text
        text = self.resolve_cell_reference(parsed["text_reference"], sheet_data)
        
        if not text:
            return "Error: Referenced cell is empty"
        
        # Call Hugging Face API
        try:
            result = await self.call_hf_api(
                text=text,
                model=parsed["model"],
                prompt=parsed["prompt"]
            )
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def call_hf_api(self, text: str, model: str, prompt: str) -> str:
        """Call Hugging Face API"""
        system_prompt = "You are a helpful and honest assistant. Please, respond concisely and truthfully."
        formatted_prompt = f"<s> [INST] {system_prompt} {prompt} {text} [/INST] </s>"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        api_url = f"https://api-inference.huggingface.co/models/{model}"
        
        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.1,
                "return_full_text": False
            }
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the generated text
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
        else:
            generated_text = str(result)
        
        return generated_text.strip()

class SheetProcessor:
    """Process entire sheets to execute HF functions"""
    
    def __init__(self, api_key: str):
        self.parser = HFFunctionParser(api_key)
    
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