"""
OCR Tool for extracting text from question sheet images and PDFs using Google Gemini.
"""
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import pathlib


class OCRToolInput(BaseModel):
    """Input schema for OCRTool."""
    file_path: str = Field(..., description="Path to the image or PDF file to perform OCR on.")


class OCRTool(BaseTool):
    """Tool for extracting text from images and PDFs using Google Gemini."""
    
    name: str = "OCR Tool"
    description: str = (
        "Extracts text from question sheet images or PDFs using Google Gemini AI. "
        "Provide the path to an image file (PNG, JPG) or PDF file and it will return the extracted text."
    )
    args_schema: Type[BaseModel] = OCRToolInput

    def _run(self, file_path: str) -> str:
        """
        Extract text from an image or PDF using Google Gemini.
        
        Args:
            file_path: Path to the image or PDF file
            
        Returns:
            Extracted text from the file
        """
        try:
            from google import genai
            from google.genai import types
            
            # Initialize client with API key
            api_key = os.environ.get("GOOGLE_API_KEY")
            client = genai.Client(api_key=api_key)
            
            # Read the file
            filepath = pathlib.Path(file_path)
            if not filepath.exists():
                return f"[OCR Tool] File not found: {file_path}"
            
            file_data = filepath.read_bytes()
            
            # Determine mime type
            file_ext = filepath.suffix.lower()
            if file_ext == '.pdf':
                mime_type = 'application/pdf'
            elif file_ext in ['.png']:
                mime_type = 'image/png'
            elif file_ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif file_ext in ['.webp']:
                mime_type = 'image/webp'
            elif file_ext in ['.gif']:
                mime_type = 'image/gif'
            else:
                mime_type = 'application/octet-stream'
            
            # Create the prompt for OCR extraction
            prompt = """Extract ALL text from this document exactly as it appears. 
This is a GSET (Gujarat State Eligibility Test) question paper.

For each question, extract:
1. Question number
2. Complete question text (preserve exact wording)
3. All options (A), (B), (C), (D) with their full text
4. Any mathematical expressions (convert to readable format)

Important:
- Extract ALL questions visible in the document
- Preserve the original numbering
- Do NOT summarize or paraphrase - extract verbatim
- If text is unclear, mark as [UNCLEAR]
- Include page numbers if visible

Output the extracted text in a structured format."""

            # Call Gemini API
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=file_data,
                        mime_type=mime_type,
                    ),
                    prompt
                ]
            )
            
            return response.text
            
        except ImportError as e:
            return f"[OCR Tool] Google GenAI not installed. Run: pip install google-genai. Error: {e}"
        except Exception as e:
            return f"[OCR Tool] Error processing file with Gemini: {str(e)}"
    
    def _process_image(self, image_path: str) -> str:
        """Extract text from an image file using Gemini."""
        return self._run(image_path)
