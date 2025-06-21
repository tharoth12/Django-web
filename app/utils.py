import warnings
import logging

# Suppress Google API warnings
warnings.filterwarnings('ignore', message='file_cache is only supported with oauth2client<4.0.0')
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os.path
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_service():
    """Get Google Sheets service using Service Account credentials"""
    try:
        # Try multiple possible paths for the credentials file
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'credentials.json'),
            os.path.join(settings.BASE_DIR, 'myenv', 'credentials.json'),
            '/home/tharoth/Django web/credentials.json',  # PythonAnywhere specific path
            '/home/tharoth/mysite/credentials.json',      # Alternative PythonAnywhere path
        ]
        
        credentials_path = None
        for path in possible_paths:
            if os.path.exists(path):
                credentials_path = path
                break
        
        if not credentials_path:
            print("Error: Credentials file not found!")
            print("Searched in the following locations:")
            for path in possible_paths:
                print(f"  - {path}")
            print("\nPlease:")
            print("1. Download your Google Service Account credentials JSON file")
            print("2. Upload it to your project root as 'credentials.json'")
            print("3. Make sure the file has the correct permissions")
            print("\nFor PythonAnywhere:")
            print("  - Upload to: /home/yourusername/Django web/credentials.json")
            print("\nFor Localhost:")
            print("  - Place in: project_root/credentials.json")
            return None
        
        print(f"Found credentials file at: {credentials_path}")
        
        # Create credentials from service account file
        creds = Credentials.from_service_account_file(
            credentials_path, 
            scopes=SCOPES
        )
        
        # Build the service
        service = build('sheets', 'v4', credentials=creds)
        print("Google Sheets service created successfully")
        return service
        
    except Exception as e:
        print(f"Error creating Google Sheets service: {str(e)}")
        print("Make sure:")
        print("1. The credentials.json file is valid and complete")
        print("2. The service account has access to the Google Sheet")
        print("3. The Google Sheet ID is correct")
        print("4. You have internet access (PythonAnywhere paid plan required)")
        return None

def append_to_sheet(booking):
    print("append_to_sheet called for booking:", booking.invoice_number)
    try:
        service = get_google_sheets_service()
        if not service:
            print("Failed to create Google Sheets service")
            return False
            
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        if not spreadsheet_id or spreadsheet_id == 'your-google-sheet-id-here':
            print("Error: GOOGLE_SHEET_ID not configured in settings")
            print("Please add GOOGLE_SHEET_ID=your-actual-sheet-id to your environment variables")
            return False
            
        range_name = 'Sheet1!A:Z'  # Adjust based on your sheet name and columns

        # First, get all existing values to check if this invoice number already exists
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        print(f"Current sheet has {len(values)} rows")
        
        # Prepare the row data
        if booking.order_type == 'rent':
            day_value = booking.return_date.strftime('%Y-%m-%d') if booking.return_date else 'N/A'
        else:
            day_value = booking.submitted_at.strftime('%Y-%m-%d')

        # Handle null invoice number
        invoice_number = booking.invoice_number or f"TEMP-{booking.id}"
        
        row_data = [
            invoice_number,                                    # Invoice Number
            booking.customer_name.title(),                     # Customer Name
            booking.phone,                                     # Phone
            booking.email.lower(),                             # Email
            booking.location.title() if booking.location else 'N/A', # Location
            booking.order_type.capitalize(),                   # Type (Rent/Buy)
            f"${booking.price:,.2f}" if booking.price else 'N/A', # Price
            booking.payment_status.replace('_', ' ').capitalize(), # Payment Status
            booking.status.capitalize(),                       # Status
            day_value,                                         # Return Day or Buy Day
        ]

        print(f"Prepared row data: {row_data}")

        # Check if this invoice number already exists
        existing_row_index = None
        for i, row in enumerate(values):
            if row and len(row) > 0 and row[0] == invoice_number:
                existing_row_index = i + 1  # Sheets API is 1-indexed
                break

        if existing_row_index:
            # Update existing row
            print(f"Updating existing row {existing_row_index} for invoice {invoice_number}")
            range_to_update = f'Sheet1!A{existing_row_index}:J{existing_row_index}'
            body = {
                'values': [row_data]
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_to_update,
                valueInputOption='RAW',
                body=body
            ).execute()
        else:
            # Append to the next available row (without inserting new rows)
            print(f"Appending to next available row for invoice {invoice_number}")
            next_row = len(values) + 1  # Next row after existing data
            
            range_to_append = f'Sheet1!A{next_row}:J{next_row}'
            body = {
                'values': [row_data]
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_to_append,
                valueInputOption='RAW',
                body=body
            ).execute()
        
        print("Google Sheets operation result:", result)
        return True
    except Exception as e:
        print(f"Error updating Google Sheet: {str(e)}")
        return False

def update_sheet_status(booking):
    """Update both status and payment status in Google Sheets"""
    try:
        service = get_google_sheets_service()
        if not service:
            print("Failed to create Google Sheets service")
            return False
            
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        if not spreadsheet_id or spreadsheet_id == 'your-google-sheet-id-here':
            print("Error: GOOGLE_SHEET_ID not configured in settings")
            print("Please add GOOGLE_SHEET_ID=your-actual-sheet-id to your environment variables")
            return False
            
        range_name = 'Sheet1!A:Z'  # Adjust based on your sheet name and columns

        # First, get all values to find the row with matching invoice number
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in Google Sheet")
            return False

        # Handle null invoice number
        invoice_number = booking.invoice_number or f"TEMP-{booking.id}"
        print(f"Looking for invoice: {invoice_number}")

        # Find the row with matching invoice number
        row_index = None
        for i, row in enumerate(values):
            if row and len(row) > 0:
                print(f"Row {i+1}: {row[0]} (looking for {invoice_number})")
                if row[0] == invoice_number:
                    row_index = i + 1  # Sheets API is 1-indexed
                    break

        if row_index is None:
            print(f"Could not find row for invoice {invoice_number}")
            print("Available invoice numbers in sheet:")
            for i, row in enumerate(values[:10]):  # Show first 10 rows
                if row and len(row) > 0:
                    print(f"  Row {i+1}: {row[0]}")
            return False

        # Update both status (column I, index 8) and payment status (column H, index 7)
        range_to_update = f'Sheet1!H{row_index}:I{row_index}'  # Columns H and I
        body = {
            'values': [[
                booking.payment_status.replace('_', ' ').capitalize(),  # Payment Status (H)
                booking.status.capitalize()  # Status (I)
            ]]
        }

        print(f"Updating row {row_index} with status: {booking.status}, payment: {booking.payment_status}")

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_to_update,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"Updated Google Sheets for invoice {invoice_number}: Status={booking.status}, Payment={booking.payment_status}")
        return True
    except Exception as e:
        print(f"Error updating Google Sheet status: {str(e)}")
        return False

def update_payment_status(booking):
    """Update only payment status in Google Sheets"""
    try:
        service = get_google_sheets_service()
        if not service:
            print("Failed to create Google Sheets service")
            return False
            
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        if not spreadsheet_id or spreadsheet_id == 'your-google-sheet-id-here':
            print("Error: GOOGLE_SHEET_ID not configured in settings")
            print("Please add GOOGLE_SHEET_ID=your-actual-sheet-id to your environment variables")
            return False
            
        range_name = 'Sheet1!A:Z'  # Adjust based on your sheet name and columns

        # First, get all values to find the row with matching invoice number
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            print("No data found in Google Sheet")
            return False

        # Handle null invoice number
        invoice_number = booking.invoice_number or f"TEMP-{booking.id}"
        print(f"Looking for invoice: {invoice_number}")

        # Find the row with matching invoice number
        row_index = None
        for i, row in enumerate(values):
            if row and len(row) > 0 and row[0] == invoice_number:
                row_index = i + 1  # Sheets API is 1-indexed
                break

        if row_index is None:
            print(f"Could not find row for invoice {invoice_number}")
            return False

        # Update only payment status (column H, index 7)
        range_to_update = f'Sheet1!H{row_index}'  # Column H is payment status
        body = {
            'values': [[booking.payment_status.replace('_', ' ').capitalize()]]
        }

        print(f"Updating payment status for row {row_index}: {booking.payment_status}")

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_to_update,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"Updated payment status in Google Sheets for invoice {invoice_number}: {booking.payment_status}")
        return True
    except Exception as e:
        print(f"Error updating Google Sheet payment status: {str(e)}")
        return False

def update_invoice_number_in_sheet(booking):
    """Update invoice number in Google Sheets when it gets generated"""
    try:
        service = get_google_sheets_service()
        if not service:
            print("Failed to create Google Sheets service")
            return False
            
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        if not spreadsheet_id or spreadsheet_id == 'your-google-sheet-id-here':
            print("Error: GOOGLE_SHEET_ID not configured in settings")
            return False
            
        range_name = 'Sheet1!A:Z'

        # Get all values to find the row
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return False

        # Look for the row with TEMP-{booking.id} or the old invoice number
        row_index = None
        temp_invoice = f"TEMP-{booking.id}"
        
        for i, row in enumerate(values):
            if row and len(row) > 0:
                if row[0] == temp_invoice or row[0] == booking.invoice_number:
                    row_index = i + 1
                    break

        if row_index is None:
            print(f"Could not find row for booking {booking.id}")
            return False

        # Update the invoice number (column A)
        range_to_update = f'Sheet1!A{row_index}'
        body = {
            'values': [[booking.invoice_number]]
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_to_update,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"Updated invoice number in Google Sheets: {booking.invoice_number}")
        return True
    except Exception as e:
        print(f"Error updating invoice number in Google Sheet: {str(e)}")
        return False 