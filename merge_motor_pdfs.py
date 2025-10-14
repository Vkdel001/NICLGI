#!/usr/bin/env python3
"""
Motor Insurance PDF Merger
Combines all PDF files from output_motor folder into a single merged PDF
"""

import os
import glob
from datetime import datetime

try:
    # Try newer pypdf first
    from pypdf import PdfWriter, PdfReader
    print("Using pypdf library")
except ImportError:
    try:
        # Fall back to PyPDF4
        from PyPDF4 import PdfFileWriter as PdfWriter, PdfFileReader as PdfReader
        print("Using PyPDF4 library")
    except ImportError:
        # Fall back to PyPDF2
        from PyPDF2 import PdfFileWriter as PdfWriter, PdfFileReader as PdfReader
        print("Using PyPDF2 library")

def test_pdf_files():
    """Test individual PDF files to check if they're readable"""
    input_folder = "output_motor"
    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found to test")
        return
    
    print(f"\n🔍 Testing {len(pdf_files)} PDF files...")
    
    for i, pdf_file in enumerate(pdf_files[:5], 1):  # Test first 5 files
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PdfReader(file)
                num_pages = len(pdf_reader.pages)
                print(f"✅ {os.path.basename(pdf_file)}: {num_pages} pages")
                
                # Try to read first page content
                if num_pages > 0:
                    first_page = pdf_reader.pages[0]
                    # Just check if we can access the page without error
                    _ = first_page.mediabox
                    
        except Exception as e:
            print(f"❌ {os.path.basename(pdf_file)}: Error - {str(e)}")

def merge_motor_pdfs():
    """Merge all PDFs from output_motor folder into a single PDF"""
    
    # Define folders
    input_folder = "output_motor"
    output_folder = "merged_motor_policies"
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"❌ Error: Input folder '{input_folder}' not found!")
        print("Please run the Motor_Insurance_Renewal.py script first to generate PDFs.")
        return
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output folder: {output_folder}")
    
    # Find all PDF files in the input folder
    pdf_files = glob.glob(os.path.join(input_folder, "*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in '{input_folder}' folder!")
        return
    
    # Sort PDF files by name for consistent ordering
    pdf_files.sort()
    
    print(f"📄 Found {len(pdf_files)} PDF files to merge")
    
    # Create merged PDF filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_filename = f"Merged_Motor_Policies_{timestamp}.pdf"
    merged_filepath = os.path.join(output_folder, merged_filename)
    
    # Create PDF writer object
    pdf_writer = PdfWriter()
    total_pages = 0
    
    # Process each PDF file
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"📖 Processing {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
            
            # Open and read the PDF file
            with open(pdf_file, 'rb') as file:
                pdf_reader = PdfReader(file)
                
                # Check if PDF has pages
                num_pages = len(pdf_reader.pages)
                if num_pages == 0:
                    print(f"⚠️ Skipping {pdf_file}: No pages found")
                    continue
                
                print(f"   📄 Adding {num_pages} pages from this PDF")
                
                # Add all pages from this PDF to the merged PDF
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        pdf_writer.add_page(page)
                        total_pages += 1
                    except Exception as page_error:
                        print(f"   ⚠️ Error adding page {page_num + 1}: {str(page_error)}")
                        continue
                    
        except Exception as e:
            print(f"⚠️ Error processing {pdf_file}: {str(e)}")
            continue
    
    # Write the merged PDF
    try:
        with open(merged_filepath, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        print(f"✅ Successfully merged {len(pdf_files)} PDFs!")
        print(f"📄 Merged PDF saved as: {merged_filepath}")
        print(f"📊 Total pages in merged PDF: {total_pages}")
        
        # Verify the output file
        if os.path.exists(merged_filepath):
            file_size = os.path.getsize(merged_filepath)
            print(f"📏 File size: {file_size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error saving merged PDF: {str(e)}")

if __name__ == "__main__":
    print("🔄 Starting PDF merge process...")
    
    # First test a few PDF files
    test_pdf_files()
    
    # Then proceed with merge
    merge_motor_pdfs()
    print("🎉 PDF merge process completed!")