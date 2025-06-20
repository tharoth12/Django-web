from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_sheets_service():
    creds = None
    token_path = os.path.join(settings.BASE_DIR, 'myenv', 'tokenemailandtelegram.txt')
    credentials_path = os.path.join(settings.BASE_DIR, 'myenv', 'credentials.json')
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)

def append_to_sheet(booking):
    try:
        service = get_google_sheets_service()
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        range_name = 'Sheet1!A:Z'  # Adjust based on your sheet name and columns

        # Only include important fields: Invoice Number, Customer Name, Phone, Email, Location, Type, Price, Payment Status, Status, Return Day/Buy Day
        if booking.order_type == 'rent':
            day_value = booking.return_date.strftime('%Y-%m-%d') if booking.return_date else 'N/A'
        else:
            day_value = booking.submitted_at.strftime('%Y-%m-%d')

        row_data = [
            booking.invoice_number,                                 # Invoice Number
            booking.customer_name.title(),                         # Customer Name
            booking.phone,                                         # Phone
            booking.email.lower(),                                 # Email
            booking.location.title() if booking.location else 'N/A', # Location
            booking.order_type.capitalize(),                       # Type (Rent/Buy)
            f"${booking.price:,.2f}",                            # Price
            booking.payment_status.replace('_', ' ').capitalize(), # Payment Status
            booking.status.capitalize(),                           # Status
            day_value,                                             # Return Day or Buy Day
        ]

        body = {
            'values': [row_data]
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()

        return True
    except Exception as e:
        print(f"Error appending to Google Sheet: {str(e)}")
        return False

def update_sheet_status(booking):
    try:
        service = get_google_sheets_service()
        spreadsheet_id = settings.GOOGLE_SHEET_ID
        range_name = 'Sheet1!A:Z'  # Adjust based on your sheet name and columns

        # First, get all values to find the row with matching invoice number
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return False

        # Find the row with matching invoice number
        row_index = None
        for i, row in enumerate(values):
            if row and row[0] == booking.invoice_number:
                row_index = i + 1  # Sheets API is 1-indexed
                break

        if row_index is None:
            return False

        # Only update the value in the status column (column I, index 8)
        range_to_update = f'Sheet1!I{row_index}'  # Column I is the status column
        body = {
            'values': [[booking.status.capitalize()]]
        }

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_to_update,
            valueInputOption='RAW',
            body=body
        ).execute()

        return True
    except Exception as e:
        print(f"Error updating Google Sheet status: {str(e)}")
        return False 