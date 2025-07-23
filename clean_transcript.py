#!/usr/bin/env python3
"""
Clean up existing transcript files by extracting only the transcript text

This utility helps clean transcript files that contain API response metadata,
extracting only the actual transcript text for better readability.

Usage:
    python clean_transcript.py input_file.txt
    python clean_transcript.py input_file.txt output_file.txt

Features:
- Extracts clean transcript text from API responses
- Removes metadata and formatting artifacts
- Handles multiple transcript segments
- Provides preview of cleaned content
"""

import re
import sys
import os

def clean_transcript_file(input_file, output_file=None):
    """Clean up transcript file by extracting only the transcript text"""
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        return
    
    if not output_file:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_clean.txt"
    
    print(f"Cleaning transcript: {input_file}")
    print(f"Output file: {output_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all transcript content
    transcript_parts = []
    
    # Find all transcript='...' patterns
    pattern = r"transcript='([^']*?)'"
    matches = re.findall(pattern, content)
    
    for match in matches:
        # Replace \\n with actual newlines
        clean_text = match.replace('\\n', '\n')
        transcript_parts.append(clean_text)
    
    # Join all parts
    clean_transcript = '\n\n'.join(transcript_parts)
    
    # Save clean transcript
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(clean_transcript)
    
    print(f"✓ Clean transcript saved to: {output_file}")
    print(f"✓ Extracted {len(transcript_parts)} transcript segments")
    
    # Show preview
    print("\n" + "="*50)
    print("CLEAN TRANSCRIPT PREVIEW:")
    print("="*50)
    preview = clean_transcript[:500] + "..." if len(clean_transcript) > 500 else clean_transcript
    print(preview)
    print("="*50)
    
    return output_file

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter transcript file to clean: ").strip()
    
    if not input_file:
        print("Error: No input file specified")
        sys.exit(1)
    
    clean_transcript_file(input_file)

if __name__ == "__main__":
    main()
