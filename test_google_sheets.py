#!/usr/bin/env python
"""
Test script to verify Google Sheets integration
Run this with: python test_google_sheets.py
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Djangoweb.settings')
django.setup()

from app.utils import get_google_sheets_service
from django.conf import settings

def test_google_sheets():
    print("=" * 50)
    print("Testing Google Sheets Integration")
    print("=" * 50)
    
    print(f"\n1. Environment Check:")
    print(f"   - Environment: {getattr(settings, 'ENVIRONMENT', 'Not set')}")
    print(f"   - Debug: {getattr(settings, 'DEBUG', 'Not set')}")
    print(f"   - GOOGLE_SHEET_ID: {getattr(settings, 'GOOGLE_SHEET_ID', 'Not set')}")
    
    # Check if credentials file exists
    credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
    print(f"\n2. Credentials File Check:")
    print(f"   - Looking for: {credentials_path}")
    print(f"   - File exists: {os.path.exists(credentials_path)}")
    
    if not os.path.exists(credentials_path):
        print("\n   ❌ CREDENTIALS FILE NOT FOUND!")
        print("   Please download your Google Service Account credentials JSON file")
        print("   and save it as 'credentials.json' in the project root folder")
        print("\n   Steps to fix:")
        print("   1. Go to Google Cloud Console")
        print("   2. Create a Service Account")
        print("   3. Download the JSON key file")
        print("   4. Rename it to 'credentials.json'")
        print("   5. Place it in the project root folder")
        return False
    
    print("\n3. Testing Service Creation:")
    try:
        service = get_google_sheets_service()
        if service:
            print("   ✅ Google Sheets service created successfully")
        else:
            print("   ❌ Failed to create Google Sheets service")
            return False
    except Exception as e:
        print(f"   ❌ Error creating service: {str(e)}")
        return False
    
    print("\n4. Testing Sheet Access:")
    try:
        # Try to read the sheet
        result = service.spreadsheets().values().get(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range='A1:Z1'  # Just read the first row
        ).execute()
        
        values = result.get('values', [])
        if values:
            print("   ✅ Successfully accessed Google Sheet")
            print(f"   - Sheet has {len(values)} rows in first range")
        else:
            print("   ⚠️ Sheet is empty or no data found")
            
    except Exception as e:
        print(f"   ❌ Error accessing sheet: {str(e)}")
        if "404" in str(e):
            print("   - Sheet not found. Check the GOOGLE_SHEET_ID")
        elif "403" in str(e):
            print("   - Permission denied. Make sure the service account has access to the sheet")
        return False
    
    print("\n5. Testing Write Operation:")
    try:
        # Try to append a test row
        test_data = [['TEST', 'Integration', 'Working', '2025-06-19']]
        result = service.spreadsheets().values().append(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range='A:Z',  # Append to the end
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': test_data}
        ).execute()
        
        print("   ✅ Successfully wrote test data to sheet")
        print(f"   - Updated range: {result.get('updates', {}).get('updatedRange', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Error writing to sheet: {str(e)}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Google Sheets Integration Test PASSED!")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_google_sheets()
    if not success:
        print("\n❌ Test failed. Please fix the issues above.")
        sys.exit(1) 