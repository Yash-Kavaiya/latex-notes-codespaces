"""
GSET Question Bank Generator Crew
=================================
A multi-agent system for processing question sheets into a professional LaTeX book.

Pipeline:
1. OCR Specialist → Extract questions from images
2. Answer Analyst → Match with answers and generate explanations  
3. Content Formatter → Create markdown chapters
4. LaTeX Book Creator → Compile final book

Author: Yash Kavaiya
Website: https://gsetexam.blogspot.com/
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool, DirectoryReadTool, FileWriterTool
from typing import List, Optional
import os
from datetime import datetime

# Import custom tools
from gset_question_bank.tools.ocr_tool import OCRTool
from gset_question_bank.tools.latex_tool import LaTeXCompilerTool, MarkdownToLaTeXTool


@CrewBase
class GsetQuestionBank():
    """
    GSET Question Bank Generator Crew
    
    This crew processes question sheet images and generates a comprehensive
    LaTeX question bank book with the following pipeline:
    
    1. OCR Extraction: Extract questions from images
    2. Answer Matching: Match with answer keys and generate explanations
    3. Markdown Generation: Create formatted chapter files
    4. LaTeX Compilation: Generate the final book
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    # Configuration paths
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        """Initialize the crew with required directories."""
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary output directories if they don't exist."""
        directories = [
            'input/question_sheets',
            'input/answer_keys',
            'output/extracted_questions',
            'output/chapters',
            'output/book'
        ]
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)

    # =========================================================================
    # LIFECYCLE HOOKS
    # =========================================================================
    
    @before_kickoff
    def prepare_inputs(self, inputs: dict) -> dict:
        """
        Prepare and validate inputs before crew execution.
        
        Args:
            inputs: Dictionary containing:
                - image_path: Path to question sheet image
                - answer_key_file: Path to answer key file
                - chapter_number: Chapter number for the book
                - chapter_name: Name of the chapter
                - subject: Subject name
                - exam_name: Name of the exam (e.g., "GSET")
        
        Returns:
            Enhanced inputs dictionary with additional metadata
        """
        # Set defaults
        inputs.setdefault('exam_name', 'GSET')
        inputs.setdefault('current_date', datetime.now().strftime('%Y-%m-%d'))
        inputs.setdefault('author', 'Yash Kavaiya')
        
        # Extract filename from image path for output naming
        if 'image_path' in inputs:
            filename = os.path.splitext(os.path.basename(inputs['image_path']))[0]
            inputs['filename'] = filename
        
        # Validate required inputs
        required_fields = ['image_path', 'chapter_number', 'chapter_name', 'subject']
        missing = [f for f in required_fields if f not in inputs]
        if missing:
            raise ValueError(f"Missing required inputs: {missing}")
        
        print(f"\n{'='*60}")
        print(f"🚀 GSET Question Bank Generator")
        print(f"{'='*60}")
        print(f"📄 Processing: {inputs.get('image_path')}")
        print(f"📚 Chapter: {inputs.get('chapter_number')} - {inputs.get('chapter_name')}")
        print(f"📖 Subject: {inputs.get('subject')}")
        print(f"{'='*60}\n")
        
        return inputs

    @after_kickoff
    def log_completion(self, result):
        """
        Log completion and provide summary after crew execution.
        
        Args:
            result: The result from crew execution
        """
        print(f"\n{'='*60}")
        print(f"✅ GSET Question Bank Generation Complete!")
        print(f"{'='*60}")
        print(f"📁 Output files generated in:")
        print(f"   • output/extracted_questions/")
        print(f"   • output/chapters/")
        print(f"   • output/book/")
        print(f"\n📘 Next Steps:")
        print(f"   1. Review generated markdown in output/chapters/")
        print(f"   2. Compile LaTeX: cd output/book && pdflatex main.tex")
        print(f"   3. Run twice for TOC: pdflatex main.tex")
        print(f"{'='*60}\n")
        
        return result

    # =========================================================================
    # TOOLS INITIALIZATION
    # =========================================================================
    
    def _get_ocr_tools(self) -> List:
        """Get tools for OCR specialist agent."""
        return [
            OCRTool(),
            FileWriterTool(),
        ]
    
    def _get_analyst_tools(self) -> List:
        """Get tools for answer analyst agent."""
        return [
            FileReadTool(),
            DirectoryReadTool(directory='input/answer_keys'),
            FileWriterTool(),
        ]
    
    def _get_formatter_tools(self) -> List:
        """Get tools for content formatter agent."""
        return [
            FileReadTool(),
            FileWriterTool(),
        ]
    
    def _get_latex_tools(self) -> List:
        """Get tools for LaTeX book creator agent."""
        return [
            FileReadTool(),
            DirectoryReadTool(directory='output/chapters'),
            FileWriterTool(),
            MarkdownToLaTeXTool(),
            LaTeXCompilerTool(),
        ]

    # =========================================================================
    # AGENT DEFINITIONS
    # =========================================================================

    @agent
    def ocr_specialist(self) -> Agent:
        """
        OCR Specialist Agent
        
        Responsible for extracting text from question sheet images with
        high accuracy and zero hallucinations.
        """
        return Agent(
            config=self.agents_config['ocr_specialist'],
            tools=self._get_ocr_tools(),
            verbose=True,
            memory=True,
            max_rpm=10,  # Rate limiting for API calls
        )

    @agent
    def answer_analyst(self) -> Agent:
        """
        Answer Analyst Agent
        
        Responsible for matching questions with correct answers and
        generating comprehensive explanations.
        """
        return Agent(
            config=self.agents_config['answer_analyst'],
            tools=self._get_analyst_tools(),
            verbose=True,
            memory=True,
        )

    @agent
    def content_formatter(self) -> Agent:
        """
        Content Formatter Agent
        
        Responsible for creating properly structured markdown files
        for each chapter with consistent formatting.
        """
        return Agent(
            config=self.agents_config['content_formatter'],
            tools=self._get_formatter_tools(),
            verbose=True,
            memory=True,
        )

    @agent
    def latex_book_creator(self) -> Agent:
        """
        LaTeX Book Creator Agent
        
        Responsible for compiling all chapters into a professional
        LaTeX question bank book with GSET branding.
        """
        return Agent(
            config=self.agents_config['latex_book_creator'],
            tools=self._get_latex_tools(),
            verbose=True,
            memory=True,
        )

    # =========================================================================
    # TASK DEFINITIONS
    # =========================================================================

    @task
    def ocr_extraction_task(self) -> Task:
        """
        Task 1: OCR Extraction
        
        Extract all questions from the input image and save as JSON.
        """
        return Task(
            config=self.tasks_config['ocr_extraction_task'],
        )

    @task
    def answer_matching_task(self) -> Task:
        """
        Task 2: Answer Matching
        
        Match extracted questions with answers and generate explanations.
        """
        return Task(
            config=self.tasks_config['answer_matching_task'],
        )

    @task
    def markdown_generation_task(self) -> Task:
        """
        Task 3: Markdown Generation
        
        Convert matched Q&A to formatted markdown chapter.
        """
        return Task(
            config=self.tasks_config['markdown_generation_task'],
        )

    @task
    def latex_book_compilation_task(self) -> Task:
        """
        Task 4: LaTeX Book Compilation
        
        Compile all chapters into the final LaTeX book.
        """
        return Task(
            config=self.tasks_config['latex_book_compilation_task'],
        )

    # =========================================================================
    # CREW CONFIGURATION
    # =========================================================================

    @crew
    def crew(self) -> Crew:
        """
        Creates the GSET Question Bank Generator Crew
        
        Process: Sequential
        - Each task depends on the output of the previous task
        - Ensures proper data flow through the pipeline
        
        Returns:
            Configured Crew instance
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            },
            # Planning enabled for complex task coordination
            planning=True,
            # Full output for detailed results
            full_output=True,
        )


# =============================================================================
# ALTERNATIVE: Hierarchical Crew Configuration
# =============================================================================

class GsetQuestionBankHierarchical(GsetQuestionBank):
    """
    Alternative hierarchical crew configuration with a manager agent.
    
    Use this when you need more dynamic task delegation and
    coordination between agents.
    """
    
    @agent
    def project_manager(self) -> Agent:
        """
        Project Manager Agent (for hierarchical process)
        
        Coordinates all other agents and ensures quality control.
        """
        return Agent(
            role="GSET Question Bank Project Manager",
            goal="Coordinate the creation of high-quality question bank materials",
            backstory="""You are an experienced project manager specializing in 
            educational content creation. You ensure quality, consistency, and 
            timely delivery of all materials.""",
            verbose=True,
            allow_delegation=True,
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the hierarchical GSET Question Bank Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.project_manager(),
            verbose=True,
            memory=True,
        )