import os
import unittest
from unittest.mock import patch
from src.sorter import Sorter

class TestPdfContentReader(unittest.TestCase):

    @patch('src.sorter.Sorter.load_mapping')
    def test_scan_and_print_content(self, mock_load_mapping):
        """
        A diagnostic test to read a specific PDF and print its extracted text.
        This uses the full text extraction logic, including the OCR fallback.
        """
        # --- INSTRUCTIONS ---
        # 1. Place the PDF you want to test into the 'tests/test_pdfs_pristine' folder.
        # 2. Change the filename below to match the name of your PDF.
        PDF_TO_TEST = "Contract.pdf"  # <--- CHANGE THIS FILENAME

        # --- SETUP ---
        # Mock the mapping load so we can initialize the Sorter without a real mapping file.
        mock_load_mapping.return_value = {}
        
        # Construct the full path to the PDF to be tested.
        pdf_path = os.path.join('tests', 'test_pdfs_pristine', PDF_TO_TEST)

        # Check if the specified file actually exists.
        if not os.path.exists(pdf_path):
            self.fail(
                f"\n\n--- ERROR: Test PDF not found ---\n"
                f"File '{PDF_TO_TEST}' was not found in the 'tests/test_pdfs_pristine' folder.\n"
                f"Please follow the setup instructions in this test file.\n"
            )

        # Initialize the sorter. We pass 'print' as the status callback to see live progress.
        sorter = Sorter('dummy_mapping.json', status_callback=print)

        # --- EXECUTION & OUTPUT ---
        print(f"\n--- Reading text from: {pdf_path} ---")
        extracted_text = sorter.read_pdf_text(pdf_path)

        # Print the final extracted text in a clearly marked block.
        print("\n" + "="*20 + " EXTRACTED TEXT START " + "="*20)
        print(extracted_text)
        print("="*22 + " EXTRACTED TEXT END " + "="*22 + "\n")

        # A simple assertion to make this a valid test for the test runner.
        self.assertIsInstance(extracted_text, str, "The extracted content should be a string.")

if __name__ == '__main__':
    unittest.main()