import os
import unittest
from unittest.mock import patch
from src.sorter import Sorter

class TestRealPdfReader(unittest.TestCase):

    @patch('src.sorter.utils.MappingUtils.load_mapping')
    def test_read_my_pdf(self, mock_load_mapping):
        """
        Reads a real PDF file specified by the user and prints its content.
        """
        # --- INSTRUCTIONS ---
        # 1. Make sure you have created a 'test_pdfs' folder in your project root.
        # 2. Place the PDF you want to test inside that folder.
        # 3. Change the filename below to match your PDF file.
        PDF_TO_TEST = "contract.pdf"  # <--- CHANGE THIS FILENAME

        # --- SETUP ---
        # Mock mapping to allow Sorter to initialize without a real mapping file
        mock_load_mapping.return_value = {}
        sorter = Sorter('dummy_mapping.json')
        
        # Construct the full path to the PDF
        pdf_path = os.path.join('test_pdfs', PDF_TO_TEST)

        # Check if the file exists before trying to read it
        if not os.path.exists(pdf_path):
            self.fail(
                f"\n\n--- ERROR: Test PDF not found ---\n"
                f"File '{PDF_TO_TEST}' was not found in the 'test_pdfs' folder.\n"
                f"Please follow the setup instructions in the test file.\n"
            )

        # --- EXECUTION & OUTPUT ---
        print(f"\n--- Reading text from: {pdf_path} ---")
        extracted_text = sorter.read_pdf_text(pdf_path)

        # Print the extracted text so you can see what the sorter reads
        print("--- Extracted Text ---")
        print(extracted_text)
        print("------------------------\n")

        # --- ASSERTION ---
        # A simple assertion to make this a valid test
        self.assertIsInstance(extracted_text, str, "The extracted content should be a string.")
        if not extracted_text:
            print("--- WARNING: No text was extracted from the PDF. It might be an image-based PDF. ---")