#!/usr/bin/env python3
"""
Motor Insurance Renewal Notice Generator
Generates 2-page motor insurance renewal notices with KYC declaration
"""

import os
import sys
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4

print("🚀 LOGO TEST: Motor_Insurance_Renewal.py script started!")
print(f"📁 Script location: {__file__}")
print(f"📁 Working directory: {os.getcwd()}")
print(f"📄 NICLOGO.jpg exists: {os.path.exists('NICLOGO.jpg')}")
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph

import pandas as pd
import requests
import segno

# Verify font files exist
cambria_regular_path = os.path.join(os.path.dirname(__file__), 'fonts', 'cambria.ttf')
cambria_bold_path = os.path.join(os.path.dirname(__file__), 'fonts', 'cambriab.ttf')

if not os.path.isfile(cambria_regular_path):
    raise FileNotFoundError(f"Font file not found: {cambria_regular_path}")
if not os.path.isfile(cambria_bold_path):
    raise FileNotFoundError(f"Font file not found: {cambria_bold_path}")

# Register Cambria fonts
try:
    pdfmetrics.registerFont(TTFont('Cambria', cambria_regular_path))
    pdfmetrics.registerFont(TTFont('Cambria-Bold', cambria_bold_path))
    print("[OK] Cambria (from cambria.ttf) and Cambria-Bold (from cambriab.ttf) fonts registered successfully")
except Exception as e:
    print(f"[ERROR] Failed to register Cambria fonts: {str(e)}")
    sys.exit(1)

# PDF Configuration
width, height = A4
margin = 50

def create_motor_renewal_pdf():
    """Create Motor Insurance Renewal Notice PDFs from Excel data"""
    
    # Create output directory
    output_dir = "output_motor"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # Read Excel file
    try:
        df = pd.read_excel('output_motor_renewal.xlsx')
        print(f"📊 Loaded {len(df)} records from output_motor_renewal.xlsx")
    except FileNotFoundError:
        print("❌ Error: output_motor_renewal.xlsx not found!")
        return
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return
    
    # Process each row
    for index, row in df.iterrows():
        try:
            # Helper function to safely get and clean data
            def safe_get(column_name, default=''):
                value = row.get(column_name, default)
                if pd.isna(value) or value is None:
                    return default
                return str(value).strip()
            
            # Validate New Net Premium - skip record if non-numeric
            new_net_premium_raw = safe_get('New Net Premium')
            try:
                # Try to convert to float to check if it's numeric
                float(new_net_premium_raw.replace(',', ''))  # Remove commas for validation
                is_numeric_premium = True
            except (ValueError, AttributeError):
                is_numeric_premium = False
            
            if not is_numeric_premium or not new_net_premium_raw.strip():
                print(f"⚠️ Skipping record {index+1}: Non-numeric or empty 'New Net Premium' value: '{new_net_premium_raw}' for {safe_get('Title')} {safe_get('Firstname')} {safe_get('Surname')}")
                continue
            
            # Map Excel columns to policy data
            policy_data = {
                'date': datetime.now().strftime('%d %B %Y'),  # System Date
                'title': safe_get('Title'),
                'firstname': safe_get('Firstname'),
                'surname': safe_get('Surname'),
                'name': f"{safe_get('Title')} {safe_get('Firstname')} {safe_get('Surname')}".strip(),
                'address1': safe_get('Address1'),
                'address2': safe_get('Address2'),
                'address3': safe_get('Address2 after Rating Category'),
                'designation': f"{safe_get('Title')} {safe_get('Firstname')} {safe_get('Surname')}".strip(),
                'policy_no': safe_get('Policy No'),
                'cover_end_dt': safe_get('Cover End Dt'),
                'make': safe_get('Make'),
                'model': safe_get('Model'),
                'vehicle_no': safe_get('Vehicle No'),
                'chassis_no': safe_get('Chassis No'),
                'compulsory_excess': safe_get('Compulsory Excess'),
                'idv': safe_get('IDV'),
                'revised_idv': safe_get('Revised IDV'),
                'new_net_premium': new_net_premium_raw,
                'nic': safe_get('NIC Number'),
                'business_type': safe_get('Business Type'),
                'old_policy_no': safe_get('Old Policy No')
            }
            
            # Calculate renewal dates based on Cover End Dt
            try:
                # Parse Cover End Dt (assuming it's in a standard date format)
                cover_end_str = policy_data['cover_end_dt']
                if cover_end_str:
                    # Try different date and datetime formats
                    date_formats = [
                        '%Y-%m-%d %H:%M:%S',  # 2025-12-03 23:59:00
                        '%Y-%m-%d %H:%M',     # 2025-12-03 23:59
                        '%Y-%m-%d',           # 2025-12-03
                        '%d/%m/%Y %H:%M:%S',  # 03/12/2025 23:59:00
                        '%d/%m/%Y %H:%M',     # 03/12/2025 23:59
                        '%d/%m/%Y',           # 03/12/2025
                        '%d-%m-%Y %H:%M:%S',  # 03-12-2025 23:59:00
                        '%d-%m-%Y %H:%M',     # 03-12-2025 23:59
                        '%d-%m-%Y',           # 03-12-2025
                        '%d %B %Y',           # 03 December 2025
                        '%d %b %Y'            # 03 Dec 2025
                    ]
                    
                    cover_end_date = None
                    for date_format in date_formats:
                        try:
                            cover_end_date = datetime.strptime(cover_end_str, date_format)
                            break
                        except ValueError:
                            continue
                    
                    if cover_end_date is None:
                        # If no format works, skip this record
                        print(f"❌ Skipping record {index+1}: Could not parse Cover End Dt '{cover_end_str}' for {policy_data['name']}")
                        continue
                    
                    # Calculate renewal start (next day after cover end)
                    renewal_start_date = cover_end_date + timedelta(days=1)
                    # Calculate renewal end (1 day less than 1 year from renewal start)
                    renewal_end_date = renewal_start_date + timedelta(days=364)
                    
                    # Format dates for display
                    policy_data['expiry_date'] = cover_end_date.strftime('%d-%B-%Y')
                    policy_data['renewal_start'] = renewal_start_date.strftime('%d-%B-%Y')
                    policy_data['renewal_end'] = renewal_end_date.strftime('%d-%B-%Y')
                else:
                    # Fallback if Cover End Dt is empty
                    policy_data['expiry_date'] = safe_get('Expiry Date')
                    policy_data['renewal_start'] = safe_get('Renewal Start')
                    policy_data['renewal_end'] = safe_get('Renewal End')
            except Exception as e:
                print(f"⚠️ Error calculating renewal dates for {policy_data['name']}: {str(e)}")
                # Fallback to original columns
                policy_data['expiry_date'] = safe_get('Expiry Date')
                policy_data['renewal_start'] = safe_get('Renewal Start')
                policy_data['renewal_end'] = safe_get('Renewal End')
            
            # Create vehicle description
            vehicle_desc = f"COMPREHENSIVE COVER\n{policy_data['make']} {policy_data['model']}\n{policy_data['vehicle_no']}\n{policy_data['chassis_no']}"
            policy_data['vehicle_desc'] = vehicle_desc
            
            # Generate PDF filename in output_motor folder with enhanced character cleaning
            import re
            # Clean name by removing/replacing problematic characters
            safe_name = policy_data['name']
            # Replace common problematic characters
            safe_name = safe_name.replace('â€"', '-')  # Replace em dash
            safe_name = safe_name.replace('–', '-')    # Replace en dash
            safe_name = safe_name.replace('—', '-')    # Replace em dash
            safe_name = safe_name.replace('"', '')     # Remove quotes
            safe_name = safe_name.replace('"', '')     # Remove smart quotes left
            safe_name = safe_name.replace('"', '')     # Remove smart quotes right
            safe_name = safe_name.replace("'", '')     # Remove smart apostrophes
            safe_name = safe_name.replace('`', '')     # Remove backticks
            # Remove any remaining non-ASCII characters and replace with underscore
            safe_name = re.sub(r'[^\x00-\x7F]+', '_', safe_name)
            # Replace spaces and path separators
            safe_name = safe_name.replace(' ', '_').replace('/', '_').replace('\\', '_')
            # Remove multiple consecutive underscores
            safe_name = re.sub(r'_+', '_', safe_name)
            # Remove leading/trailing underscores
            safe_name = safe_name.strip('_')
            
            # Truncate name if too long to prevent Windows path length issues
            max_name_length = 100  # Leave room for prefix, policy number, and extension
            if len(safe_name) > max_name_length:
                safe_name = safe_name[:max_name_length]
            
            safe_policy = policy_data['policy_no'].replace('/', '_').replace('\\', '_')
            
            # Create filename and check total path length
            base_filename = f"Motor_Renewal_{safe_name}_{safe_policy}.pdf"
            pdf_filename = os.path.join(output_dir, base_filename)
            
            # If path is still too long, truncate further
            if len(pdf_filename) > 250:  # Leave some buffer under 260 char limit
                # Calculate how much to truncate
                excess = len(pdf_filename) - 250
                new_name_length = max(20, len(safe_name) - excess)  # Minimum 20 chars for name
                safe_name = safe_name[:new_name_length]
                base_filename = f"Motor_Renewal_{safe_name}_{safe_policy}.pdf"
                pdf_filename = os.path.join(output_dir, base_filename)
            
            # Generate QR Code for payment using API
            try:
                # Create full_name for API (first letter of first name + surname, max 24 chars)
                first_initial = policy_data['firstname'][0].upper() if policy_data['firstname'] and len(policy_data['firstname']) > 0 else ''
                surname_part = policy_data['surname'].strip() if policy_data['surname'] else ''
                
                # Combine and ensure max 24 characters
                if first_initial and surname_part:
                    full_name_temp = f"{first_initial} {surname_part}"
                    full_name = full_name_temp[:24] if len(full_name_temp) > 24 else full_name_temp
                elif surname_part:
                    full_name = surname_part[:24] if len(surname_part) > 24 else surname_part
                else:
                    full_name = ''
                
                # Get mobile number and amount for QR code
                mobile_no = safe_get('Mobile No', '')
                amount = safe_get('New Net Premium', '0')
                policy_no_api = policy_data['policy_no'].replace('/', '.').replace('-', '..') if policy_data['policy_no'] else ''
                
                payload = {
                    "MerchantId": 155,
                    "SetTransactionAmount": True,
                    "TransactionAmount": str(amount),
                    "SetConvenienceIndicatorTip": False,
                    "ConvenienceIndicatorTip": 0,
                    "SetConvenienceFeeFixed": False,
                    "ConvenienceFeeFixed": 0,
                    "SetConvenienceFeePercentage": False,
                    "ConvenienceFeePercentage": 0,
                    "SetAdditionalBillNumber": True,
                    "AdditionalRequiredBillNumber": False,
                    "AdditionalBillNumber": str(policy_no_api),
                    "SetAdditionalMobileNo": True,
                    "AdditionalRequiredMobileNo": False,
                    "AdditionalMobileNo": str(mobile_no),
                    "SetAdditionalStoreLabel": False,
                    "AdditionalRequiredStoreLabel": False,
                    "AdditionalStoreLabel": "",
                    "SetAdditionalLoyaltyNumber": False,
                    "AdditionalRequiredLoyaltyNumber": False,
                    "AdditionalLoyaltyNumber": "",
                    "SetAdditionalReferenceLabel": False,
                    "AdditionalRequiredReferenceLabel": False,
                    "AdditionalReferenceLabel": "",
                    "SetAdditionalCustomerLabel": True,
                    "AdditionalRequiredCustomerLabel": False,
                    "AdditionalCustomerLabel": str(full_name),
                    "SetAdditionalTerminalLabel": False,
                    "AdditionalRequiredTerminalLabel": False,
                    "AdditionalTerminalLabel": "",
                    "SetAdditionalPurposeTransaction": True,
                    "AdditionalRequiredPurposeTransaction": False,
                    "AdditionalPurposeTransaction": str(policy_data['nic'])
                }
                
                response = requests.post(
                    "https://api.zwennpay.com:9425/api/v1.0/Common/GetMerchantQR",
                    headers={"accept": "text/plain", "Content-Type": "application/json"},
                    json=payload,
                    timeout=20
                )
                
                if response.status_code == 200:
                    qr_data = str(response.text).strip()
                    if not qr_data or qr_data.lower() in ('null', 'none', 'nan'):
                        print(f"⚠️ No valid QR data received for {policy_data['name']}")
                        qr_filename = None
                    else:
                        qr = segno.make(qr_data, error='L')
                        qr_filename = f"qr_{safe_name}_{index}.png"
                        qr.save(qr_filename, scale=10, border=2, dark='#000000')
                else:
                    print(f"❌ API request failed for {policy_data['name']}: {response.status_code} - {response.text}")
                    qr_filename = None
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Network error while generating QR for {policy_data['name']}: {str(e)}")
                qr_filename = None
            except Exception as e:
                print(f"⚠️ Error generating QR for {policy_data['name']}: {str(e)}")
                qr_filename = None
            
            # Create PDF
            c = canvas.Canvas(pdf_filename, pagesize=A4)
            
            # PAGE 1 - Motor Insurance Renewal Notice
            create_page2_renewal(c, policy_data, qr_filename)
            
            # PAGE 2 - KYC Declaration
            c.showPage()
            create_page2_kyc(c, policy_data, qr_filename)
            
            # Save the PDF
            c.save()
            

            
            # Clean up QR code file
            if qr_filename and os.path.exists(qr_filename):
                os.remove(qr_filename)
            
            print(f"✅ Generated: {pdf_filename}")
            
        except Exception as e:
            print(f"❌ Error processing row {index+1}: {str(e)}")
            continue
    
    print(f"🎉 Completed processing {len(df)} records!")

def create_page2_kyc(c, data, qr_filename):
    """Create Page 2 - KYC Declaration"""
    y_pos = height - margin - 20  # Start higher to accommodate renewal confirmation
    
    # Add Renewal Confirmation section at the top of page 2
    # Renewal confirmation section
    c.setFillColor(colors.lightblue)
    c.rect(margin, y_pos - 15, width - 2 * margin, 20, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Cambria-Bold", 10)
    c.drawString(margin + 5, y_pos - 10, "RENEWAL CONFIRMATION (Section to be filled in and signed by the Policyholder):")
    y_pos -= 25
    
    # Confirmation table with proper layout
    table_width = width - 2 * margin
    col_widths = [280, 140, 100]
    row_height = 20
    
    # Header row
    c.setFillColor(colors.lightgrey)
    x_pos = margin
    headers = ["Renewal Instructions / Remarks", "Signature", "Date"]
    
    for i, header in enumerate(headers):
        c.rect(x_pos, y_pos - row_height, col_widths[i], row_height, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Cambria-Bold", 9)
        c.drawString(x_pos + 5, y_pos - 15, header)
        c.setFillColor(colors.lightgrey)
        x_pos += col_widths[i]
    
    y_pos -= row_height
    
    # Data rows
    c.setFillColor(colors.white)
    
    # Row 1: Renew as invited
    x_pos = margin
    c.rect(x_pos, y_pos - row_height, col_widths[0], row_height, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.setFont("Cambria", 9)
    c.drawString(x_pos + 5, y_pos - 15, "Renew as invited [ ] (Please Tick)")
    
    x_pos += col_widths[0]
    c.setFillColor(colors.white)
    c.rect(x_pos, y_pos - row_height, col_widths[1], row_height, fill=1, stroke=1)
    
    x_pos += col_widths[1]
    c.rect(x_pos, y_pos - row_height, col_widths[2], row_height, fill=1, stroke=1)
    
    y_pos -= row_height
    
    # Row 2: Renew with alterations
    x_pos = margin
    c.setFillColor(colors.white)
    c.rect(x_pos, y_pos - row_height, col_widths[0], row_height, fill=1, stroke=1)
    c.setFillColor(colors.black)
    c.drawString(x_pos + 5, y_pos - 15, "Renew with the following alteration/s:")
    
    x_pos += col_widths[0]
    c.setFillColor(colors.white)
    c.rect(x_pos, y_pos - row_height, col_widths[1], row_height, fill=1, stroke=1)
    
    x_pos += col_widths[1]
    c.rect(x_pos, y_pos - row_height, col_widths[2], row_height, fill=1, stroke=1)
    
    y_pos -= row_height + 30  # Extra space after renewal confirmation
    
    # Main header paragraph
    c.setFillColor(colors.black)
    c.setFont("Cambria", 10)
    c.drawString(margin, y_pos, "In line with customer due diligence provisions of the law, you are kindly requested to confirm that there is no change in")
    y_pos -= 15
    c.drawString(margin, y_pos, "your particulars, including your name, address and mobile number. In the contrary, please provide the updated KYC")
    y_pos -= 15
    c.drawString(margin, y_pos, "document(s) (copy of the ID card and Proof of address (not more than three (3) months)) along with the signed renewal")
    y_pos -= 15
    c.drawString(margin, y_pos, "notice.")
    y_pos -= 30
    
    # Customer Declaration header with blue background - increased height for better text fit
    c.setFillColor(colors.lightblue)
    c.rect(margin, y_pos - 25, width - 2 * margin, 30, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Cambria-Bold", 9)  # Slightly smaller font for better fit
    c.drawString(margin + 5, y_pos - 10, "CUSTOMER DECLARATION (Applicable only to existing customers having submitted KYC documents previously for this")
    c.drawString(margin + 5, y_pos - 22, "specific line of business and do not have any change in their particulars)")
    c.setFillColor(colors.black)
    y_pos -= 45
    
    # I/We declaration line
    c.setFont("Cambria", 10)
    c.drawString(margin, y_pos, "I/We, ___________________________________________________________________________")
    y_pos -= 20
    
    # Holder declaration line
    c.drawString(margin, y_pos, "holder(s) of National Identity Card / Passport No.(s)______________________________________________ hereby declare")
    y_pos -= 15
    c.drawString(margin, y_pos, "that:")
    y_pos -= 20
    
    # Declaration points (a) through (e) with justified alignment
    c.setFont("Cambria", 10)
    indent_letter = margin + 10  # Position for (a), (b), etc.
    indent_text = margin + 30    # Position for continuation text
    text_width = width - indent_text - margin  # Available width for justified text
    
    # Create justified paragraph style
    justified_style = ParagraphStyle(
        'Justified',
        fontName='Cambria',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        spaceAfter=6,
        leading=12
    )
    
    # Point (a)
    c.drawString(indent_letter, y_pos, "(a)")
    text_a = "there has been no change in the information and due diligence (KYC) documentation previously submitted by me/us to the Company, including details pertaining to my/our financial and professional profile and other personal details such as name, address, mobile number, occupation, status, motor vehicle details etc."
    para_a = Paragraph(text_a, justified_style)
    para_a.wrapOn(c, text_width, 100)
    para_a.drawOn(c, indent_text, y_pos - para_a.height + 10)
    y_pos -= para_a.height + 8
    
    # Point (b)
    c.drawString(indent_letter, y_pos, "(b)")
    text_b = "the statement made and the information supplied in this questionnaire are correct and there are no other facts that are relevant to the Company for assessing my/our profile(s);"
    para_b = Paragraph(text_b, justified_style)
    para_b.wrapOn(c, text_width, 100)
    para_b.drawOn(c, indent_text, y_pos - para_b.height + 10)
    y_pos -= para_b.height + 8
    
    # Point (c)
    c.drawString(indent_letter, y_pos, "(c)")
    text_c = "the premium that is being paid to the Company comes from my own savings/salary."
    para_c = Paragraph(text_c, justified_style)
    para_c.wrapOn(c, text_width, 100)
    para_c.drawOn(c, indent_text, y_pos - para_c.height + 10)
    y_pos -= para_c.height + 8
    
    # Point (d)
    c.drawString(indent_letter, y_pos, "(d)")
    text_d = "I/We agree to furnish any additional information, as may be required, during the course of this business relationship to the Company to justify whatsoever information including, but not limited to, my/our source of funds or wealth; and"
    para_d = Paragraph(text_d, justified_style)
    para_d.wrapOn(c, text_width, 100)
    para_d.drawOn(c, indent_text, y_pos - para_d.height + 10)
    y_pos -= para_d.height + 8
    
    # Point (e)
    c.drawString(indent_letter, y_pos, "(e)")
    text_e = "I/We declare that I/We do not or am/are not related to anyone who hold any position with a significant influence on public, social or governmental policy nor acting as a senior official in a state owned organization."
    para_e = Paragraph(text_e, justified_style)
    para_e.wrapOn(c, text_width, 100)
    para_e.drawOn(c, indent_text, y_pos - para_e.height + 10)
    y_pos -= para_e.height + 15
    
    # Italic note
    c.setFont("Cambria", 9)
    c.drawString(margin + 20, y_pos, "Please fill in details below if item (e) of the above declaration does not hold good:")
    y_pos -= 25
    
    # Information table with proper column widths
    table_headers = ["Name", "Address", "Contact Number", "Email", "Occupation"]
    table_width = width - 2 * margin
    row_height = 25
    left_col_width = 140  # Increased width for header column
    right_col_width = table_width - left_col_width
    
    # Draw table
    for i, header in enumerate(table_headers):
        table_y = y_pos - (i * row_height)
        
        # Draw header cell (left column) with light grey background
        c.setFillColor(colors.lightgrey)
        c.rect(margin, table_y - row_height, left_col_width, row_height, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Cambria-Bold", 9)  # Slightly smaller font to fit better
        c.drawString(margin + 5, table_y - 15, header)
        
        # Draw data cell (right column)
        c.setFillColor(colors.white)
        c.rect(margin + left_col_width, table_y - row_height, right_col_width, row_height, fill=1, stroke=1)
    
    y_pos -= len(table_headers) * row_height + 30
    
    # Signature line
    c.setFillColor(colors.black)
    c.setFont("Cambria", 10)
    c.drawString(margin, y_pos, "Signature(s): _________________________________ Date: _____________")
    y_pos -= 60
    
    # Footer text
    c.setFont("Cambria", 9)
    footer_text = "This is a computer-generated document and requires no signature"
    text_width = c.stringWidth(footer_text, "Cambria", 9)
    c.drawString((width - text_width) / 2, y_pos, footer_text)

def create_page2_renewal(c, data, qr_filename):
    """Create Page 1 - Motor Insurance Renewal Notice"""
    # Add NIC logo at the top center of page 1 (using healthcare working method)
    print("🎯 LOGO DEBUG: create_page2_renewal function executing")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📄 NICLOGO.jpg exists: {os.path.exists('NICLOGO.jpg')}")
    
    if os.path.exists("NICLOGO.jpg"):
        from reportlab.lib.utils import ImageReader
        nic_logo_img = ImageReader("NICLOGO.jpg")
        nic_logo_width = 100  # Reduced from 120 to 100 for better fit
        nic_logo_height = nic_logo_width * (nic_logo_img.getSize()[1] / nic_logo_img.getSize()[0])
        nic_logo_x = (width - nic_logo_width) / 2  # Center horizontally
        nic_logo_y = height - nic_logo_height - 20  # Top of page (healthcare method)
        c.drawImage(nic_logo_img, nic_logo_x, nic_logo_y, width=nic_logo_width, height=nic_logo_height)
        
        # Start content below the NIC logo with reduced gap
        y_pos = nic_logo_y - 8  # Reduced from 12 to 8 for tighter spacing
    else:
        print(f"❌ Warning: NICLOGO.jpg not found - skipping NIC logo")
        y_pos = height - margin
    
    # Header with custom blue background to match the original
    custom_blue = colors.Color(70/255, 130/255, 180/255)  # Steel blue color similar to attachment
    c.setFillColor(custom_blue)
    c.rect(margin, y_pos - 20, width - 2 * margin, 25, fill=1, stroke=1)
    c.setFillColor(colors.white)
    c.setFont("Cambria-Bold", 12)
    header_text = "MOTOR INSURANCE RENEWAL NOTICE"
    text_width = c.stringWidth(header_text, "Cambria-Bold", 12)
    c.drawString((width - text_width) / 2, y_pos - 15, header_text)
    c.setFillColor(colors.black)
    y_pos -= 40
    
    # Date
    c.setFont("Cambria", 10)
    c.drawString(margin, y_pos, data['date'])
    y_pos -= 20
    
    # Address
    c.drawString(margin, y_pos, data['name'])
    y_pos -= 12
    c.drawString(margin, y_pos, data['address1'])
    y_pos -= 12
    if data['address2']:
        c.drawString(margin, y_pos, data['address2'])
        y_pos -= 12
    if data['address3']:
        c.drawString(margin, y_pos, data['address3'])
        y_pos -= 12
    y_pos -= 8
    
    # Salutation - use "Dear Valued Customer" for corporate customers (when Title is blank)
    if data['title'].strip():  # If Title exists (individual customer)
        salutation = f"Dear {data['designation']}"
    else:  # If Title is blank (corporate customer)
        salutation = "Dear Valued Customer"
    
    c.drawString(margin, y_pos, salutation)
    y_pos -= 20
    
    # Policy details - dynamic subject based on Business Type
    c.setFont("Cambria-Bold", 10)
    
    # Build subject line based on Business Type
    business_type = data['business_type'].strip().lower() if data['business_type'] else ''
    
    if business_type == 'renewed' and data['old_policy_no'].strip():
        # Renewed policy: show both old and new policy numbers
        subject_line = f"Re: Motor Insurance Policy No.: {data['old_policy_no']} – New Policy No.: {data['policy_no']}"
    elif business_type == 'new policy':
        # New policy: show only new policy number
        subject_line = f"Re: Motor Insurance Policy No.: {data['policy_no']}"
    else:
        # Default fallback: show current policy number
        subject_line = f"Re: Motor Insurance Policy No.: {data['policy_no']}"
    
    c.drawString(margin, y_pos, subject_line)
    y_pos -= 20
    
    # Main content
    c.setFont("Cambria", 10)
    main_text = f"We wish to inform you that your PRIVATE MOTOR Insurance Policy is expiring on {data['expiry_date']}. We are pleased to invite you to renew your insurance cover for the period {data['renewal_start']} to {data['renewal_end']} on the following terms:"
    
    # Create justified paragraph for main content
    justified_style_main = ParagraphStyle(
        'JustifiedMain',
        fontName='Cambria',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        spaceAfter=6,
        leading=12
    )
    
    para_main = Paragraph(main_text, justified_style_main)
    para_main.wrapOn(c, width - 2 * margin, 100)
    para_main.drawOn(c, margin, y_pos - para_main.height + 10)
    y_pos -= para_main.height + 10
    
    # Vehicle details table
    table_headers = ["Vehicle Description", "Compulsory Excess (MUR)", "Expiring IDV (MUR)", "Proposed IDV (MUR)", "Renewal Premium (MUR)"]
    table_data = [data['vehicle_desc'], data['compulsory_excess'], data['idv'], data['revised_idv'], data['new_net_premium']]
    
    # Draw table with proper spacing to match text justification width
    table_width = width - 2 * margin
    col_widths = [140, 85, 85, 85, 100]  # Adjusted to match text width exactly
    header_height = 30
    data_height = 50
    
    # Draw table header
    c.setFillColor(colors.lightgrey)
    x_pos = margin
    for i, header in enumerate(table_headers):
        c.rect(x_pos, y_pos - header_height, col_widths[i], header_height, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Cambria-Bold", 8)
        
        # Wrap header text for better fit
        if "Compulsory" in header:
            c.drawString(x_pos + 2, y_pos - 10, "Compulsory Excess")
            c.drawString(x_pos + 2, y_pos - 20, "(MUR)")
        elif "Expiring" in header:
            c.drawString(x_pos + 2, y_pos - 10, "Expiring IDV (MUR)")
            c.drawString(x_pos + 2, y_pos - 20, "Note 2")
        elif "Proposed" in header:
            c.drawString(x_pos + 2, y_pos - 10, "Proposed IDV (MUR)")
            c.drawString(x_pos + 2, y_pos - 20, "Note 2")
        elif "Renewal" in header:
            c.drawString(x_pos + 2, y_pos - 10, "Renewal Premium")
            c.drawString(x_pos + 2, y_pos - 20, "(MUR) - Note 1")
        else:
            c.drawString(x_pos + 2, y_pos - 15, header)
        
        c.setFillColor(colors.lightgrey)
        x_pos += col_widths[i]
    
    y_pos -= header_height
    
    # Draw table data
    c.setFillColor(colors.white)
    x_pos = margin
    for i, cell_data in enumerate(table_data):
        c.rect(x_pos, y_pos - data_height, col_widths[i], data_height, fill=1, stroke=1)
        c.setFillColor(colors.black)
        c.setFont("Cambria", 8)
        
        if i == 0:  # Vehicle description - multi-line
            lines = cell_data.split('\n')
            for j, line in enumerate(lines):
                c.drawString(x_pos + 3, y_pos - 12 - (j * 10), line)
        else:
            # Center other data
            text_width = c.stringWidth(str(cell_data), "Cambria", 8)
            text_x = x_pos + (col_widths[i] - text_width) / 2
            c.drawString(text_x, y_pos - 25, str(cell_data))
        
        c.setFillColor(colors.white)
        x_pos += col_widths[i]
    
    y_pos -= data_height + 20
    
    # Notes section with justified formatting
    c.setFillColor(colors.black)
    text_width_page1 = width - 2 * margin  # Full width for page 1 paragraphs
    
    # Create justified paragraph style for page 1
    justified_style_page1 = ParagraphStyle(
        'JustifiedPage1',
        fontName='Cambria',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        spaceAfter=6,
        leading=12
    )
    
    # Note 1 with justified text
    c.setFont("Cambria-Bold", 9)
    c.drawString(margin, y_pos, "Note 1: ")
    # Calculate the width of "Note 1: " label to position text after it
    note1_label_width = c.stringWidth("Note 1: ", "Cambria-Bold", 9)
    note1_text = "The Renewal Premium, which includes applicable fees and charges, is valid as at the date of this letter and may be subject to change in case of any claim intimation arising post issuance of this letter and prior expiry of the present cover."
    para_note1 = Paragraph(note1_text, justified_style_page1)
    para_note1.wrapOn(c, text_width_page1 - note1_label_width, 100)
    para_note1.drawOn(c, margin + note1_label_width, y_pos - para_note1.height + 9)
    y_pos -= para_note1.height + 10
    
    # Note 2 with justified text
    c.setFont("Cambria-Bold", 9)
    c.drawString(margin, y_pos, "Note 2: ")
    # Calculate the width of "Note 2: " label to position text after it
    note2_label_width = c.stringWidth("Note 2: ", "Cambria-Bold", 9)
    note2_text = "The Proposed Insured's Declared Value (\"IDV\") of the vehicle, including accessories if any fitted thereon, will be deemed to be the 'Sum Insured' for the Motor Insurance Policy and will be the amount insured for your vehicle. It will be the basis to determine the total loss settlements in the event the vehicle is stolen or damaged beyond repair in an accident. However, you will be compensated only for a sum equivalent to the Current Market Value of the insured vehicle at the time of loss and will not be more than the Proposed IDV."
    para_note2 = Paragraph(note2_text, justified_style_page1)
    para_note2.wrapOn(c, text_width_page1 - note2_label_width, 100)
    para_note2.drawOn(c, margin + note2_label_width, y_pos - para_note2.height + 9)
    y_pos -= para_note2.height + 10
    
    # Additional paragraphs with justified text
    para1_text = "The Proposed IDV set above is based on a depreciation rate applied to the Expiring IDV. As client, you may wish to review the Proposed IDV and obtain the Current Market Value of the vehicle from an independent Surveyor at your own cost. As Insurer, we recommend that you insure your vehicle at its Current Market Value by taking into consideration all the factors which determine its market value including, but not limited to, its age, mileage and current condition, inclusive of all taxes and charges."
    para1 = Paragraph(para1_text, justified_style_page1)
    para1.wrapOn(c, text_width_page1, 100)
    para1.drawOn(c, margin, y_pos - para1.height + 9)
    y_pos -= para1.height + 5
    
    para2_text = "Should you wish to insure your vehicle under different terms, you are kindly invited to fill in the table below and to contact us within two weeks prior to expiry of the current Policy."
    para2 = Paragraph(para2_text, justified_style_page1)
    para2.wrapOn(c, text_width_page1, 100)
    para2.drawOn(c, margin, y_pos - para2.height + 9)
    y_pos -= para2.height + 15
    
    para3_text = "*Any outstanding balance on the expiring policy will need to be settled as at the renewal date."
    para3 = Paragraph(para3_text, justified_style_page1)
    para3.wrapOn(c, text_width_page1, 100)
    para3.drawOn(c, margin, y_pos - para3.height + 9)
    y_pos -= para3.height + 5
    
    para4_text = "For any assistance, please feel free to contact us at the nearest branch office or your Insurance Advisor. Alternatively, you may call us on 602-3385."
    para4 = Paragraph(para4_text, justified_style_page1)
    para4.wrapOn(c, text_width_page1, 100)
    para4.drawOn(c, margin, y_pos - para4.height + 9)
    y_pos -= para4.height + 5
    
    # Add QR code payment instruction
    para5_text = "For your convenience, you may also settle payments instantly via the MauCAS QR Code (Scan to Pay) below using any mobile banking app such as Juice, MauBank WithMe, Blink, MyT Money, or other supported applications."
    para5 = Paragraph(para5_text, justified_style_page1)
    para5.wrapOn(c, text_width_page1, 100)
    para5.drawOn(c, margin, y_pos - para5.height + 9)
    y_pos -= para5.height + 8
    
    # Add logo and QR code vertically stacked and center aligned (compact spacing)
    logo_qr_y_position = y_pos + 10  # Move the entire logo stack up with proper spacing
    page_center_x = width / 2
    
    # Add maucas logo image (centered horizontally) - smaller size
    if os.path.exists("maucas2.jpeg"):
        from reportlab.lib.utils import ImageReader
        img = ImageReader("maucas2.jpeg")
        img_width = 100  # Optimal size for page fit
        img_height = img_width * (img.getSize()[1] / img.getSize()[0])
        # Center the logo horizontally
        logo_x = page_center_x - (img_width / 2)
        c.drawImage(img, logo_x, logo_qr_y_position - img_height, width=img_width, height=img_height)
        logo_qr_y_position -= img_height + 3  # Reduced spacing

    # Add QR code below logo (centered horizontally) - reduced size for more space
    if qr_filename and os.path.exists(qr_filename):
        qr_size = 80  # Reduced from 100 to 80 for more space
        # Center the QR code horizontally
        qr_x = page_center_x - (qr_size / 2)
        c.drawImage(qr_filename, qr_x, logo_qr_y_position - qr_size, width=qr_size, height=qr_size)
        logo_qr_y_position -= qr_size + 3  # Reduced spacing
        
        # Add ZwennPay logo below QR code (centered horizontally)
        if os.path.exists("zwennPay.jpg"):
            zwenn_img = ImageReader("zwennPay.jpg")
            zwenn_width = 70  # Optimal size for page fit
            zwenn_height = zwenn_width * (zwenn_img.getSize()[1] / zwenn_img.getSize()[0])
            # Center the ZwennPay logo horizontally
            zwenn_x = page_center_x - (zwenn_width / 2)
            c.drawImage(zwenn_img, zwenn_x, logo_qr_y_position - zwenn_height, width=zwenn_width, height=zwenn_height)
            logo_qr_y_position -= zwenn_height + 3
        

    
    y_pos = logo_qr_y_position - 5  # Reduced spacing after logo/QR stack

if __name__ == "__main__":
    print("🚗 Generating Motor Insurance Renewal Notice...")
    create_motor_renewal_pdf()
    print("✅ Motor Insurance Renewal Notice generated successfully!")