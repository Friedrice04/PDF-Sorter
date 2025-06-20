import os
import shutil
import unittest
from src.sorter import Sorter

class TestDryRun(unittest.TestCase):

    def setUp(self):
        """Set up the test environment by creating a dummy mapping file."""
        self.pristine_dir = "tests/test_pdfs_pristine"
        self.mappings_dir = "tests/mappings"
        self.mapping_path = os.path.join(self.mappings_dir, "dummy_mapping.json")

        os.makedirs(self.mappings_dir, exist_ok=True)

        # Use the mapping from your last request
        with open(self.mapping_path, "w") as f:
            f.write('{"Terms & Conditions of Employment": "Contract", "Employee Questionnaire": "Questionnaire"}')

    def tearDown(self):
        """Clean up the dummy mapping directory."""
        if os.path.exists(self.mappings_dir):
            shutil.rmtree(self.mappings_dir)

    def test_indicate_sort_destination(self):
        """
        Performs a dry run, indicating where files would be sorted without moving them.
        """
        # --- Arrange ---
        if not os.path.exists(self.pristine_dir) or not os.listdir(self.pristine_dir):
            self.skipTest(f"The '{self.pristine_dir}' directory is empty. Skipping test.")

        # Initialize the Sorter with the test mapping file.
        sorter = Sorter(self.mapping_path, status_callback=lambda msg: None) # Suppress status messages
        
        print("\n--- Starting Sorting Dry Run ---")
        print(f"Reading PDFs from: {self.pristine_dir}")
        print(f"Using mapping: {self.mapping_path}\n")

        # --- Act & Assert ---
        pdf_files = [f for f in os.listdir(self.pristine_dir) if f.lower().endswith('.pdf')]
        
        for filename in pdf_files:
            pdf_path = os.path.join(self.pristine_dir, filename)
            
            # 1. Read the text from the PDF (includes OCR fallback)
            text = sorter.read_pdf_text(pdf_path)
            
            # 2. Find the destination without moving the file
            destination = sorter.find_destination(text)
            
            # 3. Print the result
            if destination:
                print(f"-> '{filename}' would be sorted to folder: '{destination}'")
            else:
                print(f"-> '{filename}' -> No match found.")
        
        print("\n--- Dry Run Complete. No files were moved. ---")

        # Final assertion to prove no files were moved
        for filename in pdf_files:
            self.assertTrue(
                os.path.exists(os.path.join(self.pristine_dir, filename)),
                f"File '{filename}' was moved or deleted, but it should not have been."
            )

if __name__ == '__main__':
    unittest.main()