#!/usr/bin/env python
"""
GSET Question Bank Generator - Main Entry Point
================================================

This script provides multiple ways to run the question bank generation crew:
1. Single file processing
2. Batch processing (multiple images)
3. Interactive mode
4. Training and testing modes

Author: Yash Kavaiya
Website: https://gsetexam.blogspot.com/
YouTube: https://youtube.com/playlist?list=PL6gpvClXEwJXRbutffBm0bjAwKfoaNlMw
"""

import sys
import os
import warnings
import json
import glob
from datetime import datetime
from pathlib import Path

from gset_question_bank.crew import GsetQuestionBank, GsetQuestionBankHierarchical

# Suppress unnecessary warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


# =============================================================================
# CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    'exam_name': 'GSET',
    'author': 'Yash Kavaiya',
    'website': 'https://gsetexam.blogspot.com/',
    'youtube': 'https://youtube.com/playlist?list=PL6gpvClXEwJXRbutffBm0bjAwKfoaNlMw',
    'telegram': 't.me/gset_exam',
    'facebook': 'https://www.facebook.com/GSETEXAM/',
}


# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def run():
    """
    Run the crew with default/example inputs.
    
    Usage:
        crewai run
        or
        python -m gset_question_bank.main
    """
    inputs = {
        'image_path': 'input/question_sheets/sample_question_paper.png',
        'answer_key_file': 'input/answer_keys/sample_answer_key.txt',
        'chapter_number': 1,
        'chapter_name': 'Sample Chapter',
        'subject': 'General Studies',
        'exam_name': DEFAULT_CONFIG['exam_name'],
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        **DEFAULT_CONFIG
    }

    print_banner()
    
    try:
        result = GsetQuestionBank().crew().kickoff(inputs=inputs)
        print_success(result)
        return result
    except Exception as e:
        print_error(f"An error occurred while running the crew: {e}")
        raise


def run_single(
    image_path: str,
    answer_key_file: str,
    chapter_number: int,
    chapter_name: str,
    subject: str
):
    """
    Process a single question sheet image.
    
    Args:
        image_path: Path to the question sheet image
        answer_key_file: Path to the answer key file
        chapter_number: Chapter number for the book
        chapter_name: Name of the chapter
        subject: Subject name
    
    Returns:
        Crew execution result
    
    Usage:
        from gset_question_bank.main import run_single
        run_single('path/to/image.png', 'path/to/answers.txt', 1, 'Chapter 1', 'Math')
    """
    inputs = {
        'image_path': image_path,
        'answer_key_file': answer_key_file,
        'chapter_number': chapter_number,
        'chapter_name': chapter_name,
        'subject': subject,
        'exam_name': DEFAULT_CONFIG['exam_name'],
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        **DEFAULT_CONFIG
    }

    print_banner()
    
    try:
        result = GsetQuestionBank().crew().kickoff(inputs=inputs)
        print_success(result)
        return result
    except Exception as e:
        print_error(f"An error occurred: {e}")
        raise


def run_batch(config_file: str = 'batch_config.json'):
    """
    Process multiple question sheets in batch mode.
    
    The config file should be a JSON file with structure:
    {
        "chapters": [
            {
                "image_path": "input/question_sheets/ch1.png",
                "answer_key_file": "input/answer_keys/ch1_answers.txt",
                "chapter_number": 1,
                "chapter_name": "Introduction",
                "subject": "General Studies"
            },
            ...
        ]
    }
    
    Args:
        config_file: Path to batch configuration JSON file
    
    Returns:
        List of results for each chapter
    """
    print_banner()
    print(f"📋 Loading batch configuration from: {config_file}")
    
    if not os.path.exists(config_file):
        print_error(f"Config file not found: {config_file}")
        return None
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    chapters = config.get('chapters', [])
    total = len(chapters)
    results = []
    
    print(f"📚 Found {total} chapters to process\n")
    
    for idx, chapter in enumerate(chapters, 1):
        print(f"\n{'='*60}")
        print(f"Processing Chapter {idx}/{total}: {chapter.get('chapter_name', 'Unknown')}")
        print(f"{'='*60}")
        
        inputs = {
            **chapter,
            'exam_name': config.get('exam_name', DEFAULT_CONFIG['exam_name']),
            'current_date': datetime.now().strftime('%Y-%m-%d'),
            **DEFAULT_CONFIG
        }
        
        try:
            result = GsetQuestionBank().crew().kickoff(inputs=inputs)
            results.append({'chapter': chapter, 'result': result, 'status': 'success'})
            print(f"✅ Chapter {idx} completed successfully")
        except Exception as e:
            results.append({'chapter': chapter, 'result': None, 'status': 'error', 'error': str(e)})
            print_error(f"Chapter {idx} failed: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    
    return results


def run_interactive():
    """
    Interactive mode for processing question sheets.
    
    Prompts user for input parameters and processes accordingly.
    """
    print_banner()
    print("🎯 Interactive Mode\n")
    
    # Get inputs from user
    print("Please provide the following information:\n")
    
    image_path = input("📄 Question sheet image path: ").strip()
    if not image_path:
        image_path = input("   (or drag & drop the file here): ").strip()
    
    answer_key_file = input("🔑 Answer key file path: ").strip()
    
    chapter_number = input("📚 Chapter number [1]: ").strip()
    chapter_number = int(chapter_number) if chapter_number else 1
    
    chapter_name = input("📖 Chapter name: ").strip()
    if not chapter_name:
        chapter_name = f"Chapter {chapter_number}"
    
    subject = input("📝 Subject name: ").strip()
    if not subject:
        subject = "General Studies"
    
    # Confirm
    print(f"\n{'='*40}")
    print("📋 Configuration Summary:")
    print(f"{'='*40}")
    print(f"  Image: {image_path}")
    print(f"  Answer Key: {answer_key_file}")
    print(f"  Chapter: {chapter_number} - {chapter_name}")
    print(f"  Subject: {subject}")
    print(f"{'='*40}")
    
    confirm = input("\nProceed? [Y/n]: ").strip().lower()
    if confirm and confirm != 'y':
        print("❌ Cancelled")
        return None
    
    return run_single(image_path, answer_key_file, chapter_number, chapter_name, subject)


def compile_book():
    """
    Compile all generated chapters into the final LaTeX book.
    
    This function is useful when you've already generated chapters
    and just want to compile them into a book.
    """
    print_banner()
    print("📚 Compiling LaTeX Book\n")
    
    chapters_dir = 'output/chapters'
    book_dir = 'output/book'
    
    # Find all chapter files
    chapter_files = sorted(glob.glob(f'{chapters_dir}/chapter_*.md'))
    
    if not chapter_files:
        print_error(f"No chapter files found in {chapters_dir}")
        return None
    
    print(f"Found {len(chapter_files)} chapters to compile:")
    for f in chapter_files:
        print(f"  • {os.path.basename(f)}")
    
    # Create minimal inputs for book compilation task
    inputs = {
        'exam_name': DEFAULT_CONFIG['exam_name'],
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        'chapter_files': chapter_files,
        **DEFAULT_CONFIG
    }
    
    # Run only the LaTeX compilation task
    from gset_question_bank.crew import GsetQuestionBank
    
    crew = GsetQuestionBank()
    latex_agent = crew.latex_book_creator()
    
    # TODO: Implement standalone book compilation
    print("\n⚠️  Standalone book compilation not yet implemented")
    print("Please run the full pipeline or compile manually with pdflatex")
    
    return None


# =============================================================================
# TRAINING AND TESTING
# =============================================================================

def train():
    """
    Train the crew for improved performance.
    
    Usage:
        crewai train <n_iterations> <output_file>
    """
    inputs = {
        'image_path': 'input/question_sheets/training_sample.png',
        'answer_key_file': 'input/answer_keys/training_answers.txt',
        'chapter_number': 1,
        'chapter_name': 'Training Sample',
        'subject': 'Training',
        **DEFAULT_CONFIG
    }
    
    try:
        n_iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 3
        filename = sys.argv[2] if len(sys.argv) > 2 else 'training_output.pkl'
        
        print(f"🎯 Training crew for {n_iterations} iterations...")
        GsetQuestionBank().crew().train(
            n_iterations=n_iterations,
            filename=filename,
            inputs=inputs
        )
        print(f"✅ Training complete! Output saved to {filename}")
    except Exception as e:
        print_error(f"Training failed: {e}")
        raise


def test():
    """
    Test the crew execution and evaluate results.
    
    Usage:
        crewai test <n_iterations> <eval_model>
    """
    inputs = {
        'image_path': 'input/question_sheets/test_sample.png',
        'answer_key_file': 'input/answer_keys/test_answers.txt',
        'chapter_number': 1,
        'chapter_name': 'Test Sample',
        'subject': 'Test',
        **DEFAULT_CONFIG
    }
    
    try:
        n_iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        eval_llm = sys.argv[2] if len(sys.argv) > 2 else 'gpt-4'
        
        print(f"🧪 Testing crew with {eval_llm}...")
        GsetQuestionBank().crew().test(
            n_iterations=n_iterations,
            eval_llm=eval_llm,
            inputs=inputs
        )
    except Exception as e:
        print_error(f"Testing failed: {e}")
        raise


def replay():
    """
    Replay the crew execution from a specific task.
    
    Usage:
        crewai replay <task_id>
    """
    try:
        task_id = sys.argv[1]
        print(f"🔄 Replaying from task: {task_id}")
        GsetQuestionBank().crew().replay(task_id=task_id)
    except Exception as e:
        print_error(f"Replay failed: {e}")
        raise


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ███████╗███████╗████████╗                          ║
║  ██╔════╝ ██╔════╝██╔════╝╚══██╔══╝                          ║
║  ██║  ███╗███████╗█████╗     ██║                             ║
║  ██║   ██║╚════██║██╔══╝     ██║                             ║
║  ╚██████╔╝███████║███████╗   ██║                             ║
║   ╚═════╝ ╚══════╝╚══════╝   ╚═╝                             ║
║                                                               ║
║            Question Bank Generator                            ║
║                                                               ║
║  Author: Yash Kavaiya                                         ║
║  Website: https://gsetexam.blogspot.com/                      ║
║  YouTube: Gen AI Guru                                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_success(result):
    """Print success message with result summary."""
    print(f"\n{'='*60}")
    print("🎉 SUCCESS!")
    print(f"{'='*60}")
    print(f"\n📁 Generated Files:")
    print(f"   • JSON: output/extracted_questions/")
    print(f"   • Markdown: output/chapters/")
    print(f"   • LaTeX: output/book/")
    print(f"\n📖 To generate PDF:")
    print(f"   cd output/book && pdflatex main.tex && pdflatex main.tex")
    print(f"\n{'='*60}\n")


def print_error(message: str):
    """Print error message."""
    print(f"\n❌ ERROR: {message}\n")


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'interactive':
            run_interactive()
        elif command == 'batch':
            config_file = sys.argv[2] if len(sys.argv) > 2 else 'batch_config.json'
            run_batch(config_file)
        elif command == 'compile':
            compile_book()
        elif command == 'train':
            train()
        elif command == 'test':
            test()
        elif command == 'replay':
            replay()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  interactive  - Interactive mode with prompts")
            print("  batch        - Process multiple chapters from config")
            print("  compile      - Compile existing chapters into book")
            print("  train        - Train the crew")
            print("  test         - Test the crew")
            print("  replay       - Replay from a specific task")
    else:
        run()