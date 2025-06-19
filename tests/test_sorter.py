import unittest
from unittest.mock import patch, MagicMock
from src.sorter import Sorter

# Helper function to create a mock for a fitz.Document (which is a context manager)
def create_mock_document_context(pages):
    """Creates a mock context manager that yields an iterable of mock pages."""
    mock_doc_context = MagicMock()
    # When the 'with' statement is used, __enter__ is called.
    # We make it return an iterable (list) of mock pages.
    mock_doc_context.__enter__.return_value = pages
    return mock_doc_context

class TestSorter(unittest.TestCase):

    @patch('src.sorter.utils.MappingUtils.load_mapping')
    @patch('src.sorter.fitz.open')
    def test_read_pdf_text(self, mock_fitz_open, mock_load_mapping):
        """
        Tests that read_pdf_text correctly extracts and concatenates text from a PDF.
        This test simulates reading a PDF with two pages.
        """
        # --- Arrange ---
        # 1. Mock the mapping data so the Sorter can be initialized without a real file.
        mock_load_mapping.return_value = {"keyword": "folder"}

        # 2. Create mock pages with some text.
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Text from page 1. "
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Text from page 2."
        
        # 3. Set up the mock for fitz.open to return our mock document context.
        mock_fitz_open.return_value = create_mock_document_context([mock_page1, mock_page2])

        # 4. Initialize the Sorter. The mapping path can be a dummy value.
        sorter = Sorter('dummy_mapping.json')

        # --- Act ---
        # Call the method we want to test.
        extracted_text = sorter.read_pdf_text('dummy.pdf')

        # --- Assert ---
        # Check if the extracted text is what we expect.
        expected_text = "Text from page 1. Text from page 2."
        self.assertEqual(extracted_text, expected_text)

        # To satisfy your request to "see what my sorter is reading",
        # we print the output. This will be visible when running pytest with the -s flag.
        print(f"\n--- Sorter read the following text ---\n{extracted_text}\n------------------------------------")

if __name__ == '__main__':
    unittest.main()