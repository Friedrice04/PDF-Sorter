# 🧪 PDF Test Runner

An automated testing system for PDF sorting functionality. Drop PDFs in a folder, specify mapping files, and get detailed reports on where each PDF would be sorted.

## 📁 Directory Structure

```
tests/test_runner/
├── input_pdfs/          # 📄 Drop your test PDFs here
├── test_mappings/       # 🗂️  Put your mapping JSON files here  
├── results/            # 📊 Test results and reports go here
└── run_pdf_tests.py    # 🚀 Main test runner script
```

## 🚀 Quick Start

### 1. Add Test Files
- **PDFs**: Drop any PDF files into `input_pdfs/`
- **Mappings**: Add JSON mapping files to `test_mappings/`

### 2. Run Tests
```bash
# Test all PDFs with all mappings
python run_pdf_tests.py

# Test with a specific mapping
python run_pdf_tests.py --mapping hr_test

# Get verbose output
python run_pdf_tests.py --verbose

# Save results to file
python run_pdf_tests.py --save-results
```

### 3. View Results
Results are displayed in the console and optionally saved to `results/` folder.

## 📋 Example Output

```
🧪 Running tests on 2 PDFs with 2 mappings...
📁 Input PDFs: ['contract.pdf', 'questionnaire.pdf']
🗂️  Mappings: ['hr_test_mapping.json', 'finance_test_mapping.json']

📋 Testing with mapping: hr_test_mapping.json
  ✅ contract.pdf        → 01 Pay
  ✅ questionnaire.pdf   → 03 Personnel/Personal Details

📋 Testing with mapping: finance_test_mapping.json  
  ❓ contract.pdf        → General (no match)
  ❓ questionnaire.pdf   → General (no match)

📊 PDF SORTING TEST SUMMARY
Total tests run: 4
Successful: 4
Failed: 0
Success rate: 100.0%
```

## 🎯 Features

### ✅ What It Does
- **Batch Testing**: Test multiple PDFs at once
- **Multiple Mappings**: Test same PDFs against different sorting schemes
- **Detailed Reports**: See exactly where each PDF would go and why
- **Performance Metrics**: Track processing time for each test
- **Error Handling**: Clear error messages for failed tests
- **Dry Run**: Shows where files would go without actually moving them

### 📊 Output Information
For each test, you get:
- PDF filename
- Mapping file used
- Matched phrase (if any)
- Destination folder
- Rule name that matched
- Processing time
- Text preview (first 200 characters)
- Success/error status

### 🔧 Command Line Options
```bash
python run_pdf_tests.py [OPTIONS]

Options:
  --mapping NAME     Filter to specific mapping (partial name match)
  --verbose, -v      Show detailed information during testing
  --save-results, -s Save results to JSON file in results/ folder
  --no-summary      Skip the summary report at the end
```

## 📝 Mapping File Format

Test mapping files should follow this JSON structure:

```json
{
  "config": {
    "unmatched_destination": "Unsorted",
    "case_sensitive": false,
    "naming_scheme": "{original_name}"
  },
  "rules": [
    {
      "name": "Rule Name",
      "phrase": "Text to search for",
      "destination": "Target/Folder/Path"
    }
  ]
}
```

## 🎉 Use Cases

### 🧪 **Development Testing**
- Test new mapping rules before deploying
- Verify PDF text extraction is working
- Check performance with different file types

### 📊 **Mapping Validation**  
- Test how well your mapping rules work
- Find PDFs that don't match any rules
- Compare different mapping strategies

### 🐛 **Debugging**
- See exactly what text is extracted from PDFs
- Identify why certain PDFs aren't matching
- Test OCR fallback functionality

### 📈 **Performance Analysis**
- Measure processing time for different PDF types
- Test with large batches of files
- Identify slow-processing documents

## 💡 Tips

1. **Start Small**: Test with a few PDFs first to verify everything works
2. **Use Descriptive Names**: Name your mapping files clearly (e.g., `hr_mapping.json`, `finance_mapping.json`)
3. **Check Results**: Review the detailed output to understand how matching works
4. **Save Results**: Use `--save-results` to keep detailed logs for analysis
5. **Test Edge Cases**: Include PDFs that might not match any rules

## 🔧 Troubleshooting

**No PDFs found**: Make sure PDF files are in the `input_pdfs/` directory
**No mappings found**: Add JSON mapping files to `test_mappings/` directory  
**Import errors**: Make sure you're running from the correct directory
**OCR issues**: Ensure Tesseract is installed for scanned PDF support

---

This testing system makes it super easy to validate your PDF sorting logic and experiment with different mapping strategies! 🚀
