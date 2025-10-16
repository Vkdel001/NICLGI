#!/usr/bin/env python3
"""
Motor Insurance Printer Version PDF Merger
Merges individual motor insurance renewal PDFs (printer version) into a single file
"""

import os
import sys
import glob
from datetime import datetime

try:
    # Try newer pypdf first
    from pypdf import PdfWriter, PdfReader
    print("Using pypdf library")
except ImportError:
    try:
        # Try modern PyPDF2 (3.0.0+) with correct imports
        from PyPDF2 import PdfWriter, PdfReader
        print("Using PyPDF2 library")
    except ImportError:
        try:
            # Fall back to PyPDF4
            from PyPDF4 import PdfFileWriter as PdfWriter, PdfFileReader as PdfReader
            print("Using PyPDF4 library")
        except ImportError:
            # Last resort - old PyPDF2 (should not reach here)
            from PyPDF2 import PdfFileWriter as PdfWriter, PdfFileReader as PdfReader
            print("Using old PyPDF2 library")

def merge_motor_printer_pdfs():
    """Merge all motor insurance printer version PDFs into a single file"""
    
    # Define directories
    input_dir = "output_motor_printer"
    output_dir = "merged_motor_printer_policies"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"❌ Error: Input directory '{input_dir}' not found!")
        return False
    
    # Find all PDF files in the input directory
    pdf_pattern = os.path.join(input_dir, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print(f"❌ Error: No PDF files found in '{input_dir}'!")
        return False
    
    # Sort files for consistent ordering
    pdf_files.sort()
    
    print(f"📄 Found {len(pdf_files)} PDF files to merge")
    
    # Create writer object
    writer = PdfWriter()
    
    try:
        # Add each PDF to the writer
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                print(f"📎 Adding file {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    writer.add_page(page)
            except Exception as e:
                print(f"⚠️ Warning: Could not add {pdf_file}: {str(e)}")
                continue
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Motor_Renewal_Printer_Merged_{timestamp}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Write merged PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"✅ Successfully merged {len(pdf_files)} PDFs into: {output_filename}")
        print(f"📁 Output location: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during merging: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Motor Insurance Printer Version PDF Merger...")
    success = merge_motor_printer_pdfs()
    
    if success:
        print("🎉 Merge completed successfully!")
        sys.exit(0)
    else:
        print("💥 Merge failed!")
        sys.exit(1)