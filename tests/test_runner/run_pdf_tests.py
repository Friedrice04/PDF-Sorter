#!/usr/bin/env python3
"""
PDF Test Runner - Automated PDF Sorting Test System

This script provides an easy way to test PDF sorting functionality:
1. Drop PDFs in the 'input_pdfs' folder
2. Put mapping JSON files in 'test_mappings' folder  
3. Run this script to see where each PDF would be sorted
4. Results are saved to 'results' folder and displayed in console

Usage:
    python run_pdf_tests.py [--mapping MAPPING_NAME] [--verbose] [--save-results]
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.sorter import Sorter


class PDFTestRunner:
    """Automated test runner for PDF sorting functionality."""
    
    def __init__(self, test_dir: str = None):
        """Initialize the test runner."""
        if test_dir is None:
            test_dir = Path(__file__).parent
        
        self.test_dir = Path(test_dir)
        self.input_dir = self.test_dir / "input_pdfs"
        self.mappings_dir = self.test_dir / "test_mappings"
        self.results_dir = self.test_dir / "results"
        
        # Ensure directories exist
        self.input_dir.mkdir(exist_ok=True)
        self.mappings_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        
        self.test_results = []
        
    def get_available_pdfs(self) -> List[Path]:
        """Get list of PDF files in input directory."""
        return list(self.input_dir.glob("*.pdf"))
    
    def get_available_mappings(self) -> List[Path]:
        """Get list of mapping JSON files."""
        return list(self.mappings_dir.glob("*.json"))
    
    def test_pdf_with_mapping(self, pdf_path: Path, mapping_path: Path, verbose: bool = False) -> Dict:
        """Test a single PDF with a specific mapping."""
        
        if verbose:
            print(f"  Testing: {pdf_path.name} with {mapping_path.name}")
        
        start_time = time.time()
        
        try:
            # Create sorter instance
            sorter = Sorter(str(mapping_path))
            
            # Read PDF text
            text = sorter.read_pdf_text(str(pdf_path), first_page_only=True)
            
            # Use the sorter's find_destination method to find matches
            destination = sorter.find_destination(text)
            
            # Try to find which phrase matched by checking against the mapping
            matched_phrase = None
            rule_name = None
            destination_folder = None
            
            if destination:
                # Handle both old format (string) and new format (dict)
                if isinstance(destination, dict):
                    destination_folder = destination.get('dest', 'Unknown')
                    rule_name = destination.get('name', 'Unknown Rule')
                else:
                    destination_folder = destination
                    rule_name = f"Direct mapping"
                
                # Normalize the text like the sorter does
                normalized_text = ' '.join(text.split()).lower()
                
                # Check against the mapping data to find which phrase matched
                for phrase, dest_info in sorter.mapping_data.items():
                    normalized_phrase = ' '.join(phrase.split()).lower()
                    if normalized_phrase in normalized_text:
                        if isinstance(dest_info, dict):
                            if dest_info.get('dest') == destination_folder:
                                matched_phrase = phrase
                                break
                        else:
                            if dest_info == destination_folder:
                                matched_phrase = phrase
                                break
            
            # If no match found, destination will be None
            if not destination:
                destination_folder = "Unmatched"
                rule_name = "No matching rule"
            
            processing_time = time.time() - start_time
            
            result = {
                'pdf_file': pdf_path.name,
                'mapping_file': mapping_path.name,
                'matched_phrase': matched_phrase,
                'rule_name': rule_name,
                'destination_folder': destination_folder,
                'text_preview': text[:200] + "..." if len(text) > 200 else text,
                'processing_time_ms': round(processing_time * 1000, 2),
                'success': True,
                'error': None
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            result = {
                'pdf_file': pdf_path.name,
                'mapping_file': mapping_path.name,
                'matched_phrase': None,
                'rule_name': None,
                'destination_folder': None,
                'text_preview': None,
                'processing_time_ms': round(processing_time * 1000, 2),
                'success': False,
                'error': str(e)
            }
            
        return result
    
    def run_tests(self, mapping_filter: str = None, verbose: bool = False) -> List[Dict]:
        """Run tests for all PDFs against all (or filtered) mappings."""
        
        pdfs = self.get_available_pdfs()
        mappings = self.get_available_mappings()
        
        if not pdfs:
            print("❌ No PDF files found in input_pdfs directory!")
            print(f"   Place PDF files in: {self.input_dir}")
            return []
        
        if not mappings:
            print("❌ No mapping files found in test_mappings directory!")
            print(f"   Place JSON mapping files in: {self.mappings_dir}")
            return []
        
        # Filter mappings if specified
        if mapping_filter:
            mappings = [m for m in mappings if mapping_filter.lower() in m.name.lower()]
            if not mappings:
                print(f"❌ No mappings found matching filter: {mapping_filter}")
                return []
        
        print(f"🧪 Running tests on {len(pdfs)} PDFs with {len(mappings)} mappings...")
        print(f"📁 Input PDFs: {[p.name for p in pdfs]}")
        print(f"🗂️  Mappings: {[m.name for m in mappings]}")
        print("="*60)
        
        results = []
        
        for mapping in mappings:
            print(f"\n📋 Testing with mapping: {mapping.name}")
            print("-" * 40)
            
            for pdf in pdfs:
                result = self.test_pdf_with_mapping(pdf, mapping, verbose)
                results.append(result)
                
                # Display result
                if result['success']:
                    if result['matched_phrase']:
                        print(f"  ✅ {pdf.name:<25} → {result['destination_folder']}")
                        if verbose:
                            print(f"     📝 Rule: {result['rule_name']}")
                            print(f"     🎯 Phrase: '{result['matched_phrase']}'")
                            print(f"     ⏱️  Time: {result['processing_time_ms']}ms")
                    else:
                        print(f"  ❓ {pdf.name:<25} → {result['destination_folder']} (no match)")
                else:
                    print(f"  ❌ {pdf.name:<25} → ERROR: {result['error']}")
        
        self.test_results = results
        return results
    
    def save_results(self, results: List[Dict], filename_prefix: str = "test_results") -> str:
        """Save test results to JSON file."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        report_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(results),
                'successful_tests': sum(1 for r in results if r['success']),
                'failed_tests': sum(1 for r in results if not r['success']),
                'unique_pdfs': len(set(r['pdf_file'] for r in results)),
                'unique_mappings': len(set(r['mapping_file'] for r in results))
            },
            'results': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def generate_summary_report(self, results: List[Dict]) -> str:
        """Generate a human-readable summary report."""
        
        if not results:
            return "No test results to report."
        
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        # Group by PDF
        pdf_results = {}
        for result in results:
            pdf_name = result['pdf_file']
            if pdf_name not in pdf_results:
                pdf_results[pdf_name] = []
            pdf_results[pdf_name].append(result)
        
        report = []
        report.append("📊 PDF SORTING TEST SUMMARY")
        report.append("="*50)
        report.append(f"Total tests run: {len(results)}")
        report.append(f"Successful: {len(successful)}")
        report.append(f"Failed: {len(failed)}")
        report.append(f"Success rate: {len(successful)/len(results)*100:.1f}%")
        report.append("")
        
        # Per-PDF breakdown
        report.append("📄 PER-PDF RESULTS:")
        report.append("-"*30)
        
        for pdf_name, pdf_tests in pdf_results.items():
            report.append(f"\n🔍 {pdf_name}:")
            for test in pdf_tests:
                mapping = test['mapping_file']
                if test['success']:
                    dest = test['destination_folder']
                    rule = test['rule_name']
                    report.append(f"  ✅ {mapping:<20} → {dest} ({rule})")
                else:
                    report.append(f"  ❌ {mapping:<20} → ERROR: {test['error']}")
        
        if failed:
            report.append(f"\n❌ FAILED TESTS ({len(failed)}):")
            report.append("-"*25)
            for test in failed:
                report.append(f"  {test['pdf_file']} + {test['mapping_file']}: {test['error']}")
        
        avg_time = sum(r['processing_time_ms'] for r in successful) / len(successful) if successful else 0
        report.append(f"\n⏱️  Average processing time: {avg_time:.2f}ms")
        
        return "\n".join(report)


def main():
    """Main entry point for the test runner."""
    
    parser = argparse.ArgumentParser(description="PDF Sorting Test Runner")
    parser.add_argument("--mapping", help="Filter to specific mapping file (partial name match)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--save-results", "-s", action="store_true", help="Save results to JSON file")
    parser.add_argument("--no-summary", action="store_true", help="Skip summary report")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = PDFTestRunner()
    
    # Run tests
    results = runner.run_tests(mapping_filter=args.mapping, verbose=args.verbose)
    
    if not results:
        sys.exit(1)
    
    # Show summary
    if not args.no_summary:
        print("\n" + "="*60)
        summary = runner.generate_summary_report(results)
        print(summary)
    
    # Save results if requested
    if args.save_results:
        saved_file = runner.save_results(results)
        print(f"\n💾 Results saved to: {saved_file}")
    
    print(f"\n🎉 Testing complete! Processed {len(results)} tests.")


if __name__ == "__main__":
    main()
