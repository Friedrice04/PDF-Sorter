#!/usr/bin/env python3
"""
Demo script to show PDF Test Runner capabilities.
This creates some demo files and runs a quick test.
"""

import os
import sys
from pathlib import Path

def create_demo_files():
    """Create some demo content for testing."""
    
    # Get current directory
    current_dir = Path(__file__).parent
    input_dir = current_dir / "input_pdfs"
    
    # Create a simple text file to simulate PDF testing
    demo_file = input_dir / "demo_test.txt"
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write("""
This is a demo file to test the PDF Test Runner system.

Key features tested:
- Text extraction and processing
- Phrase matching with multiple mappings  
- Detailed result reporting
- Batch processing capabilities
- Performance metrics tracking

The actual system works with real PDF files, but this demo shows
the reporting and analysis capabilities.

Demo phrases for testing:
- Employee Questionnaire (should match HR mapping)
- Invoice details (should match finance mapping)
- Training Record information
""")
    
    print(f"Created demo file: {demo_file}")
    
    # Show current test files
    pdf_files = list(input_dir.glob("*.pdf"))
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF files:")
        for pdf in pdf_files:
            print(f"   - {pdf.name}")
    
    mapping_files = list((current_dir / "test_mappings").glob("*.json"))
    print(f"Found {len(mapping_files)} mapping files:")
    for mapping in mapping_files:
        print(f"   - {mapping.name}")

def main():
    """Run the demo."""
    
    print("PDF Test Runner Demo")
    print("="*40)
    
    create_demo_files()
    
    print("\nTo run the actual tests:")
    print("1. Add PDF files to the 'input_pdfs' folder")
    print("2. Run: python run_pdf_tests.py")
    print("3. Or use the batch file: run_tests.bat")
    
    print("\nAvailable commands:")
    print("  python run_pdf_tests.py --verbose")
    print("  python run_pdf_tests.py --mapping hr_test")
    print("  python run_pdf_tests.py --save-results")
    
    print("\nThe system will show:")
    print("  - Which PDFs match which rules")
    print("  - Where each file would be sorted")
    print("  - Processing time and success rates")
    print("  - Detailed text extraction previews")

if __name__ == "__main__":
    main()
