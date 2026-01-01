"""
LaTeX Tools for compiling and converting documents.
"""
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import subprocess
import os


class LaTeXCompilerInput(BaseModel):
    """Input schema for LaTeXCompilerTool."""
    tex_file_path: str = Field(..., description="Path to the LaTeX .tex file to compile.")
    output_dir: str = Field(default="output", description="Directory to save the compiled PDF.")


class LaTeXCompilerTool(BaseTool):
    """Tool for compiling LaTeX documents to PDF."""
    
    name: str = "LaTeX Compiler"
    description: str = (
        "Compiles a LaTeX .tex file into a PDF document. "
        "Provide the path to the .tex file and optionally an output directory."
    )
    args_schema: Type[BaseModel] = LaTeXCompilerInput

    def _run(self, tex_file_path: str, output_dir: str = "output") -> str:
        """
        Compile a LaTeX file to PDF.
        
        Args:
            tex_file_path: Path to the .tex file
            output_dir: Directory for output files
            
        Returns:
            Result message indicating success or failure
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            result = subprocess.run(
                ["pdflatex", "-output-directory", output_dir, tex_file_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                pdf_name = os.path.splitext(os.path.basename(tex_file_path))[0] + ".pdf"
                pdf_path = os.path.join(output_dir, pdf_name)
                return f"Successfully compiled LaTeX to PDF: {pdf_path}"
            else:
                return f"LaTeX compilation failed: {result.stderr}"
                
        except FileNotFoundError:
            return "[LaTeX Compiler] pdflatex not found. Please install a LaTeX distribution."
        except subprocess.TimeoutExpired:
            return "[LaTeX Compiler] Compilation timed out after 120 seconds."
        except Exception as e:
            return f"[LaTeX Compiler] Error: {str(e)}"


class MarkdownToLaTeXInput(BaseModel):
    """Input schema for MarkdownToLaTeXTool."""
    markdown_content: str = Field(..., description="Markdown content to convert to LaTeX.")


class MarkdownToLaTeXTool(BaseTool):
    """Tool for converting Markdown to LaTeX format."""
    
    name: str = "Markdown to LaTeX Converter"
    description: str = (
        "Converts Markdown formatted text to LaTeX format. "
        "Useful for converting question content to LaTeX for book compilation."
    )
    args_schema: Type[BaseModel] = MarkdownToLaTeXInput

    def _run(self, markdown_content: str) -> str:
        """
        Convert Markdown content to LaTeX.
        
        Args:
            markdown_content: Markdown formatted text
            
        Returns:
            LaTeX formatted text
        """
        latex_content = markdown_content
        
        # Basic Markdown to LaTeX conversions
        conversions = [
            # Headers
            (r'^# (.+)$', r'\\chapter{\1}'),
            (r'^## (.+)$', r'\\section{\1}'),
            (r'^### (.+)$', r'\\subsection{\1}'),
            (r'^#### (.+)$', r'\\subsubsection{\1}'),
            
            # Bold and italic
            (r'\*\*(.+?)\*\*', r'\\textbf{\1}'),
            (r'\*(.+?)\*', r'\\textit{\1}'),
            
            # Code blocks
            (r'`(.+?)`', r'\\texttt{\1}'),
            
            # Lists (basic)
            (r'^- (.+)$', r'\\item \1'),
            (r'^\d+\. (.+)$', r'\\item \1'),
        ]
        
        import re
        for pattern, replacement in conversions:
            latex_content = re.sub(pattern, replacement, latex_content, flags=re.MULTILINE)
        
        return latex_content
