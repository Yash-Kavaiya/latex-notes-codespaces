"""
File Handling Tools
Author: Yash Kavaiya
"""

import json
from pathlib import Path
from typing import Type, Optional, List
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FileReaderInput(BaseModel):
    """Input for file reader tool."""
    file_path: str = Field(description="Path to the file to read")


class FileReaderTool(BaseTool):
    """Tool for reading files of various formats."""
    
    name: str = "file_reader_tool"
    description: str = "Reads content from files (JSON, MD, TXT, TEX)"
    args_schema: Type[BaseModel] = FileReaderInput
    
    def _run(self, file_path: str) -> str:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File not found at {file_path}"
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if path.suffix == '.json':
                # Pretty print JSON
                data = json.loads(content)
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"


class FileWriterInput(BaseModel):
    """Input for file writer tool."""
    filename: str = Field(description="The filename to write to (can include path)")
    directory: Optional[str] = Field(default="./", description="Directory path (optional, defaults to current dir)")
    overwrite: bool = Field(default=False, description="Whether to overwrite existing file")
    content: str = Field(description="Content to write to the file")


class FileWriterTool(BaseTool):
    """Tool for writing content to files with proper path handling."""
    
    name: str = "File Writer Tool"
    description: str = "A tool to write content to a specified file. Accepts filename, content, and optionally a directory path and overwrite flag as input."
    args_schema: Type[BaseModel] = FileWriterInput
    
    def _run(self, filename: str, content: str, directory: Optional[str] = "./", overwrite: bool = False) -> str:
        try:
            # Smart path handling - avoid double directory concatenation
            if directory and directory != "./":
                # Check if filename already contains the directory path
                if filename.startswith(directory):
                    # Filename already has directory, use as-is
                    file_path = filename
                elif filename.startswith("output/") or filename.startswith("input/") or filename.startswith("./"):
                    # Filename has a path prefix, use as-is
                    file_path = filename
                else:
                    # Combine directory and filename
                    file_path = str(Path(directory) / filename)
            else:
                file_path = filename
            
            path = Path(file_path)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists and overwrite is False
            if path.exists() and not overwrite:
                return f"File already exists at {file_path}. Set overwrite=true to replace it."
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            return f"An error occurred while writing to the file: {str(e)}"


class AnswerKeyParserInput(BaseModel):
    """Input for answer key parser."""
    answer_key_path: str = Field(description="Path to answer key file")


class AnswerKeyParserTool(BaseTool):
    """Tool for parsing answer key files."""
    
    name: str = "answer_key_parser_tool"
    description: str = """
    Parses answer key files in various formats (CSV, TXT, JSON).
    Returns a dictionary mapping question numbers to correct answers.
    """
    args_schema: Type[BaseModel] = AnswerKeyParserInput
    
    def _run(self, answer_key_path: str) -> str:
        path = Path(answer_key_path)
        if not path.exists():
            return f"Error: Answer key not found at {answer_key_path}"
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            answers = {}
            
            # Try JSON format first
            if path.suffix == '.json':
                data = json.loads(content)
                if isinstance(data, dict):
                    answers = data
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'question' in item and 'answer' in item:
                            answers[str(item['question'])] = item['answer']
            
            # Try line-by-line format (e.g., "1. A" or "1,A")
            else:
                for line in content.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Try various formats
                    for sep in ['.', ',', ':', '\t', ' ']:
                        if sep in line:
                            parts = line.split(sep, 1)
                            if len(parts) == 2:
                                q_num = parts[0].strip()
                                answer = parts[1].strip().upper()
                                if answer in ['A', 'B', 'C', 'D']:
                                    answers[q_num] = answer
                                    break
            
            return json.dumps(answers, indent=2)
        
        except Exception as e:
            return f"Error parsing answer key: {str(e)}"