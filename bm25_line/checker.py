#!/usr/bin/env python3
"""
JSONL Diagnostic and Repair Tool
Identifies and fixes common JSONL formatting issues
"""

import json
import re
from typing import List, Dict, Any, Tuple, Optional
import os
from tqdm import tqdm

class JSONLDiagnostic:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.line_count = 0
        
    def count_lines(self) -> int:
        """Count total lines in file"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    
    def diagnose_line(self, line_num: int, line: str) -> Optional[Dict[str, Any]]:
        """Diagnose a single line for JSON issues"""
        if not line.strip():
            return None
            
        try:
            # Try to parse the line as JSON
            json.loads(line)
            return None  # No error
        except json.JSONDecodeError as e:
            return {
                'line_number': line_num,
                'error_type': type(e).__name__,
                'error_message': str(e),
                'error_position': getattr(e, 'pos', None),
                'line_content': line[:200] + '...' if len(line) > 200 else line,
                'line_length': len(line)
            }
    
    def find_problematic_characters(self, line: str) -> List[Dict[str, Any]]:
        """Find characters that commonly cause JSON parsing issues"""
        issues = []
        
        # Check for unescaped quotes
        in_string = False
        escaped = False
        quote_char = None
        
        for i, char in enumerate(line):
            if escaped:
                escaped = False
                continue
                
            if char == '\\':
                escaped = True
                continue
                
            if char in ['"', "'"]:
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
                else:
                    issues.append({
                        'type': 'unescaped_quote',
                        'position': i,
                        'char': char,
                        'context': line[max(0, i-10):i+10]
                    })
        
        # Check for control characters
        for i, char in enumerate(line):
            if ord(char) < 32 and char not in ['\t']:  # Allow tabs
                issues.append({
                    'type': 'control_character',
                    'position': i,
                    'char': repr(char),
                    'ord': ord(char),
                    'context': line[max(0, i-10):i+10]
                })
        
        # Check for potential multi-line issues
        if line.count('{') != line.count('}'):
            issues.append({
                'type': 'bracket_mismatch',
                'open_brackets': line.count('{'),
                'close_brackets': line.count('}')
            })
            
        return issues
    
    def diagnose_file(self, max_errors: int = 100) -> Dict[str, Any]:
        """Diagnose the entire JSONL file"""
        print(f"Diagnosing JSONL file: {self.file_path}")
        
        total_lines = self.count_lines()
        print(f"Total lines to check: {total_lines}")
        
        errors = []
        line_errors = {}
        error_types = {}
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            pbar = tqdm(total=total_lines, desc="Checking lines")
            
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                    
                # Check for JSON parsing errors
                error = self.diagnose_line(line_num, line)
                if error:
                    errors.append(error)
                    line_errors[line_num] = error
                    
                    error_type = error['error_type']
                    error_types[error_type] = error_types.get(error_type, 0) + 1
                    
                    # Also check for character-level issues
                    char_issues = self.find_problematic_characters(line)
                    if char_issues:
                        error['character_issues'] = char_issues
                
                pbar.update(1)
                
                if len(errors) >= max_errors:
                    print(f"Reached maximum error limit ({max_errors}), stopping...")
                    break
            
            pbar.close()
        
        return {
            'total_lines': total_lines,
            'total_errors': len(errors),
            'error_rate': len(errors) / total_lines * 100,
            'errors': errors,
            'line_errors': line_errors,
            'error_types': error_types
        }
    
    def print_diagnosis_summary(self, diagnosis: Dict[str, Any]):
        """Print a summary of the diagnosis"""
        print("\n" + "="*60)
        print("JSONL DIAGNOSIS SUMMARY")
        print("="*60)
        print(f"Total lines: {diagnosis['total_lines']:,}")
        print(f"Lines with errors: {diagnosis['total_errors']:,}")
        print(f"Error rate: {diagnosis['error_rate']:.2f}%")
        
        if diagnosis['error_types']:
            print("\nError types:")
            for error_type, count in sorted(diagnosis['error_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count} occurrences")
        
        if diagnosis['errors']:
            print(f"\nFirst {min(10, len(diagnosis['errors']))} errors:")
            for i, error in enumerate(diagnosis['errors'][:10]):
                print(f"\n{i+1}. Line {error['line_number']}:")
                print(f"   Error: {error['error_message']}")
                print(f"   Content: {error['line_content']}")
                if 'character_issues' in error:
                    print(f"   Character issues: {len(error['character_issues'])}")
    
    def attempt_repair(self, output_file: str, max_attempts: int = 1000) -> Dict[str, Any]:
        """Attempt to repair common JSONL issues"""
        print(f"\nAttempting to repair JSONL file...")
        print(f"Output file: {output_file}")
        
        repaired = 0
        skipped = 0
        total_processed = 0
        
        with open(self.file_path, 'r', encoding='utf-8') as input_f, \
             open(output_file, 'w', encoding='utf-8') as output_f:
            
            for line_num, line in enumerate(tqdm(input_f, desc="Repairing lines"), 1):
                if not line.strip():
                    continue
                
                total_processed += 1
                original_line = line
                
                try:
                    # Try to parse as-is first
                    json.loads(line)
                    output_f.write(line)
                    continue
                except json.JSONDecodeError:
                    pass
                
                # Try repair strategies
                repaired_line = self.repair_line(line)
                
                if repaired_line:
                    try:
                        # Validate the repaired line
                        json.loads(repaired_line)
                        output_f.write(repaired_line)
                        if not repaired_line.endswith('\n'):
                            output_f.write('\n')
                        repaired += 1
                    except json.JSONDecodeError:
                        print(f"Failed to repair line {line_num}")
                        skipped += 1
                        if skipped < 10:  # Show first few failed repairs
                            print(f"  Original: {original_line[:100]}...")
                            print(f"  Attempted repair: {repaired_line[:100]}...")
                else:
                    skipped += 1
                
                if repaired + skipped >= max_attempts:
                    print(f"Reached maximum repair attempts ({max_attempts})")
                    break
        
        return {
            'total_processed': total_processed,
            'repaired': repaired,
            'skipped': skipped,
            'output_file': output_file
        }
    
    def repair_line(self, line: str) -> Optional[str]:
        """Attempt to repair a single line"""
        # Strategy 1: Remove control characters except tabs
        cleaned = ''.join(char for char in line if ord(char) >= 32 or char == '\t')
        
        # Strategy 2: Try to fix common escape issues
        # Fix unescaped quotes in strings
        cleaned = re.sub(r'(?<!\\)"(?=.*")', '\\"', cleaned)
        
        # Strategy 3: Remove trailing commas before closing brackets
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
        
        # Strategy 4: Ensure the line ends properly
        cleaned = cleaned.strip()
        if not cleaned.endswith('\n'):
            cleaned += '\n'
        
        return cleaned

def main():
    """Main diagnostic function"""
    jsonl_file = "../autonomous_indian_agriculture_complete.jsonl"
    
    if not os.path.exists(jsonl_file):
        print(f"Error: File {jsonl_file} not found!")
        return
    
    # Create diagnostic tool
    diagnostic = JSONLDiagnostic(jsonl_file)
    
    # Run diagnosis
    print("Starting JSONL file diagnosis...")
    diagnosis = diagnostic.diagnose_file(max_errors=50)  # Limit to first 50 errors
    
    # Print summary
    diagnostic.print_diagnosis_summary(diagnosis)
    
    # Offer to repair if errors found
    if diagnosis['total_errors'] > 0:
        response = input(f"\nFound {diagnosis['total_errors']} errors. Attempt repair? (y/n): ")
        if response.lower() == 'y':
            output_file = "../autonomous_indian_agriculture_complete_repaired.jsonl"
            repair_results = diagnostic.attempt_repair(output_file)
            
            print(f"\nRepair completed:")
            print(f"  Total processed: {repair_results['total_processed']:,}")
            print(f"  Successfully repaired: {repair_results['repaired']:,}")
            print(f"  Skipped (couldn't repair): {repair_results['skipped']:,}")
            print(f"  Output saved to: {repair_results['output_file']}")
            
            if repair_results['repaired'] > 0:
                print(f"\nYou can now try using the repaired file:")
                print(f"  Update your main.py to use: {output_file}")
    
    else:
        print("\nNo errors found! Your JSONL file appears to be properly formatted.")

if __name__ == "__main__":
    main()

