#!/usr/bin/env python3
"""
Motor Insurance Printer Version PDF Merger
Merges individual motor insurance renewal PDFs (printer version) into a single file
Uses PyMuPDF for reliable QR code and image preservation across Windows/Ubuntu
"""

import os
import sys
import glob
from datetime import datetime

try:
    import fitz  # PyMuPDF - reliable PDF handling that preserves QR codes
    print("Using PyMuPDF (fitz) library - reliable image preservation")
except ImportError:
    print("❌ PyMuPDF not installed. Please install it:")
    print("pip install PyMuPDF")
    print("\nPyMuPDF is required for reliable QR code preservation during PDF merging.")
    sys.exit(1)

def merge_motor_printer_pdfs():
    """Merge all motor insurance printer version PDFs into a single file using PyMuPDF"""
    
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
    
    try:
        # Create new merged document using PyMuPDF
        merged_doc = fitz.open()
        
        # Add each PDF to the merged document
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                print(f"📎 Adding file {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
                
                # Open source PDF
                source_doc = fitz.open(pdf_file)
                
                # Insert all pages from source PDF (preserves QR codes and all content)
                for page_num in range(source_doc.page_count):
                    merged_doc.insert_pdf(source_doc, from_page=page_num, to_page=page_num)
                
                # Close source document
                source_doc.close()
                
            except Exception as e:
                print(f"⚠️ Warning: Could not add {pdf_file}: {str(e)}")
                continue
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Motor_Renewal_Printer_Merged_{timestamp}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Save merged PDF
        merged_doc.save(output_path)
        
        # Get final page count for verification
        total_pages = merged_doc.page_count
        
        # Close merged document
        merged_doc.close()
        
        print(f"✅ Successfully merged {len(pdf_files)} PDFs into: {output_filename}")
        print(f"📁 Output location: {output_path}")
        print(f"📄 Total pages in merged PDF: {total_pages}")
        
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