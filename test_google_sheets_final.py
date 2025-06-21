#!/usr/bin/env python
"""
Final test script to verify Google Sheets integration
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/d%3A/Django%20web')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Djangoweb.settings')
django.setup()

from app.models import RentalBooking
from app.utils import get_google_sheets_service, append_to_sheet, update_sheet_status
from django.conf import settings

def test_google_sheets_configuration():
    """Test Google Sheets configuration"""
    print("=== Testing Google Sheets Configuration ===")
    
    print(f"GOOGLE_SHEET_ID: {settings.GOOGLE_SHEET_ID}")
    
    # Check credentials file
    credentials_path = os.path.join(settings.BASE_DIR, 'credentials.json')
    print(f"Credentials file exists: {os.path.exists(credentials_path)}")
    
    # Test service creation
    service = get_google_sheets_service()
    if service:
        print("✅ Google Sheets service created successfully")
        return True
    else:
        print("❌ Failed to create Google Sheets service")
        return False

def test_sheet_connection():
    """Test connection to the actual Google Sheet"""
    print("\n=== Testing Sheet Connection ===")
    
    service = get_google_sheets_service()
    if not service:
        return False
    
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=settings.GOOGLE_SHEET_ID,
            range='Sheet1!A:Z'
        ).execute()
        
        values = result.get('values', [])
        print(f"✅ Successfully connected to Google Sheet")
        print(f"📊 Sheet has {len(values)} rows")
        
        if values:
            print("📋 First few rows:")
            for i, row in enumerate(values[:3]):
                print(f"  Row {i+1}: {row}")
        
        return True
    except Exception as e:
        print(f"❌ Error connecting to Google Sheet: {str(e)}")
        return False

def test_booking_data():
    """Test booking data"""
    print("\n=== Testing Booking Data ===")
    
    bookings = RentalBooking.objects.all().order_by('-submitted_at')[:3]
    print(f"📋 Found {len(bookings)} recent bookings")
    
    for booking in bookings:
        print(f"\n🔍 Booking ID: {booking.id}")
        print(f"   Invoice: {booking.invoice_number or 'None'}")
        print(f"   Status: {booking.status}")
        print(f"   Payment: {booking.payment_status}")
        print(f"   Customer: {booking.customer_name}")
        print(f"   Price: {booking.price}")

def test_append_function():
    """Test append_to_sheet function"""
    print("\n=== Testing Append Function ===")
    
    booking = RentalBooking.objects.first()
    if booking:
        print(f"🧪 Testing with booking: {booking.invoice_number or f'TEMP-{booking.id}'}")
        
        success = append_to_sheet(booking)
        if success:
            print("✅ Successfully appended to Google Sheet")
        else:
            print("❌ Failed to append to Google Sheet")
    else:
        print("⚠️ No bookings found to test with")

def test_status_update():
    """Test status update function"""
    print("\n=== Testing Status Update ===")
    
    booking = RentalBooking.objects.first()
    if booking:
        print(f"🧪 Testing with booking: {booking.invoice_number or f'TEMP-{booking.id}'}")
        
        success = update_sheet_status(booking)
        if success:
            print("✅ Successfully updated status in Google Sheet")
        else:
            print("❌ Failed to update status in Google Sheet")
    else:
        print("⚠️ No bookings found to test with")

if __name__ == "__main__":
    print("🚀 Starting Google Sheets Integration Test...")
    
    # Test configuration
    if not test_google_sheets_configuration():
        print("❌ Configuration test failed. Please check your setup.")
        exit(1)
    
    # Test sheet connection
    if not test_sheet_connection():
        print("❌ Sheet connection test failed. Please check your Google Sheet ID and permissions.")
        exit(1)
    
    # Test booking data
    test_booking_data()
    
    # Test functions
    test_append_function()
    test_status_update()
    
    print("\n✅ Google Sheets Integration Test Complete!")
    print("\n📝 Next steps:")
    print("1. Create a new booking through the website")
    print("2. Check if it appears in Google Sheets")
    print("3. Approve the booking through admin or Telegram")
    print("4. Check if status and invoice number update in Google Sheets") 