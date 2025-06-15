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
    token_path = os.path.join(settings.BASE_DIR, 'myenv', 'token.pickle')
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

        # Improved row data formatting
        row_data = [
            booking.invoice_number,
            booking.order_type.capitalize(),
            booking.customer_name.title(),
            booking.phone,
            booking.email.lower(),
            booking.location.title() if booking.location else 'N/A',
            booking.product.title if booking.product else 'N/A',
            f"${booking.price:,.2f}",
            booking.status.capitalize(),
            booking.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'Yes' if getattr(booking, 'ats_panel', False) else 'No',
            'Yes' if getattr(booking, 'onsite_technician', False) else 'No',
            'Yes' if getattr(booking, 'power_backup_design', False) else 'No',
            f"${booking.get_total_optional_services():,.2f}" if hasattr(booking, 'get_total_optional_services') else 'N/A',
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