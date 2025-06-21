#!/usr/bin/env python3
"""
Comprehensive Test Script for Django App
Tests functionality on both localhost and PythonAnywhere environments.
Includes Google Sheets integration testing.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Djangoweb.settings')
django.setup()

from django.conf import settings
from app.utils import get_google_sheets_service, append_to_sheet
from app.models import RentalBooking, GeneralInfo
from datetime import datetime, timedelta
import requests

def test_environment_detection():
    """Test environment detection"""
    print("=" * 60)
    print("ENVIRONMENT DETECTION TEST")
    print("=" * 60)
    
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Base URL: {getattr(settings, 'BASE_URL', 'Not set')}")
    print(f"Static files storage: {settings.STATICFILES_STORAGE}")
    print(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    
    # Test environment-specific settings
    if settings.ENVIRONMENT == 'production':
        print("✅ Running in PRODUCTION mode (PythonAnywhere)")
        print(f"   SSL Redirect: {getattr(settings, 'SECURE_SSL_REDIRECT', False)}")
        print(f"   Session Cookie Secure: {getattr(settings, 'SESSION_COOKIE_SECURE', False)}")
    else:
        print("✅ Running in DEVELOPMENT mode (Localhost)")
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    try:
        # Test basic database operations
        general_info_count = GeneralInfo.objects.count()
        rental_bookings_count = RentalBooking.objects.count()
        
        print(f"✅ Database connection successful")
        print(f"   GeneralInfo records: {general_info_count}")
        print(f"   RentalBooking records: {rental_bookings_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_email_configuration():
    """Test email configuration"""
    print("\n" + "=" * 60)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    email_host_user = settings.EMAIL_HOST_USER
    email_host_password = settings.EMAIL_HOST_PASSWORD
    default_from_email = settings.DEFAULT_FROM_EMAIL
    
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Email Host User: {'✅ Set' if email_host_user else '❌ Not set'}")
    print(f"Email Host Password: {'✅ Set' if email_host_password else '❌ Not set'}")
    print(f"Default From Email: {'✅ Set' if default_from_email else '❌ Not set'}")
    
    if email_host_user and email_host_password:
        print("✅ Email configuration appears complete")
        return True
    else:
        print("❌ Email configuration incomplete")
        return False

def test_telegram_configuration():
    """Test Telegram configuration"""
    print("\n" + "=" * 60)
    print("TELEGRAM CONFIGURATION TEST")
    print("=" * 60)
    
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', 'Not set')
    
    print(f"Bot Token: {'✅ Set' if bot_token else '❌ Not set'}")
    print(f"Chat ID: {chat_id}")
    print(f"Webhook URL: {webhook_url}")
    
    if bot_token and chat_id:
        print("✅ Telegram configuration appears complete")
        return True
    else:
        print("❌ Telegram configuration incomplete")
        return False

def test_google_sheets_setup():
    """Comprehensive Google Sheets setup test"""
    print("\n" + "=" * 60)
    print("GOOGLE SHEETS INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Check environment variables
    print("\n1. Checking environment variables...")
    sheet_id = settings.GOOGLE_SHEET_ID
    print(f"   GOOGLE_SHEET_ID: {sheet_id}")
    
    if not sheet_id or sheet_id == 'your-google-sheet-id-here':
        print("   ❌ ERROR: GOOGLE_SHEET_ID not configured properly")
        print("   Please add GOOGLE_SHEET_ID=your-actual-sheet-id to your environment variables")
        return False
    else:
        print("   ✅ GOOGLE_SHEET_ID is configured")
    
    # Test 2: Check credentials file
    print("\n2. Checking credentials file...")
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'credentials.json'),
        os.path.join(settings.BASE_DIR, 'myenv', 'credentials.json'),
        '/home/tharoth/Django web/credentials.json',
        '/home/tharoth/mysite/credentials.json',
    ]
    
    credentials_found = False
    for path in possible_paths:
        if os.path.exists(path):
            print(f"   ✅ Found credentials file at: {path}")
            credentials_found = True
            break
    
    if not credentials_found:
        print("   ❌ ERROR: credentials.json file not found!")
        print("   Searched in:")
        for path in possible_paths:
            print(f"     - {path}")
        print("\n   Please upload your Google Service Account credentials JSON file")
        print("   to your project root as 'credentials.json'")
        return False
    
    # Test 3: Test service creation
    print("\n3. Testing Google Sheets service creation...")
    service = get_google_sheets_service()
    
    if not service:
        print("   ❌ ERROR: Failed to create Google Sheets service")
        return False
    else:
        print("   ✅ Google Sheets service created successfully")
    
    # Test 4: Test sheet access
    print("\n4. Testing sheet access...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='Sheet1!A1:Z1'
        ).execute()
        
        values = result.get('values', [])
        if values:
            print(f"   ✅ Successfully accessed sheet. Found {len(values[0])} columns in header row")
            print(f"   Header: {values[0]}")
        else:
            print("   ⚠️  Sheet is empty or no data found")
        
    except Exception as e:
        print(f"   ❌ ERROR accessing sheet: {str(e)}")
        print("   Make sure:")
        print("   1. The service account has access to the Google Sheet")
        print("   2. The sheet ID is correct")
        print("   3. The sheet exists and is not deleted")
        return False
    
    # Test 5: Test with a sample booking
    print("\n5. Testing with sample booking data...")
    try:
        # Create a test booking object (not saved to database)
        class TestBooking:
            def __init__(self):
                self.id = 999999
                self.invoice_number = f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                self.customer_name = "Test Customer"
                self.phone = "123-456-7890"
                self.email = "test@example.com"
                self.location = "Test Location"
                self.order_type = "rent"
                self.price = 1000.00
                self.payment_status = "pending_payment"
                self.status = "pending"
                self.return_date = datetime.now().date() + timedelta(days=30)
                self.submitted_at = datetime.now()
        
        test_booking = TestBooking()
        
        # Test append function
        success = append_to_sheet(test_booking)
        
        if success:
            print("   ✅ Successfully added test data to Google Sheet")
            print(f"   Test invoice number: {test_booking.invoice_number}")
        else:
            print("   ❌ Failed to add test data to Google Sheet")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR during test data insertion: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL GOOGLE SHEETS TESTS PASSED!")
    print("=" * 60)
    return True

def test_static_files():
    """Test static files configuration"""
    print("\n" + "=" * 60)
    print("STATIC FILES TEST")
    print("=" * 60)
    
    static_root = settings.STATIC_ROOT
    static_url = settings.STATIC_URL
    staticfiles_dirs = settings.STATICFILES_DIRS
    
    print(f"Static URL: {static_url}")
    print(f"Static Root: {static_root}")
    print(f"Static Files Dirs: {staticfiles_dirs}")
    
    # Check if static files directory exists
    for static_dir in staticfiles_dirs:
        if os.path.exists(static_dir):
            print(f"✅ Static files directory exists: {static_dir}")
        else:
            print(f"❌ Static files directory missing: {static_dir}")
    
    # Check if static root exists (for production)
    if settings.ENVIRONMENT == 'production':
        if os.path.exists(static_root):
            print(f"✅ Static root directory exists: {static_root}")
        else:
            print(f"⚠️  Static root directory missing: {static_root}")
            print("   Run 'python manage.py collectstatic' in production")
    
    return True

def test_media_files():
    """Test media files configuration"""
    print("\n" + "=" * 60)
    print("MEDIA FILES TEST")
    print("=" * 60)
    
    media_root = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL
    
    print(f"Media URL: {media_url}")
    print(f"Media Root: {media_root}")
    
    if os.path.exists(media_root):
        print(f"✅ Media directory exists: {media_root}")
    else:
        print(f"⚠️  Media directory missing: {media_root}")
        print("   This will be created automatically when needed")
    
    return True

def test_webhook_accessibility():
    """Test if webhook is accessible"""
    print("\n" + "=" * 60)
    print("WEBHOOK ACCESSIBILITY TEST")
    print("=" * 60)
    
    webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
    
    if not webhook_url:
        print("❌ Webhook URL not configured")
        return False
    
    print(f"Testing webhook URL: {webhook_url}")
    
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            print("✅ Webhook is accessible")
            return True
        else:
            print(f"❌ Webhook returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Webhook not accessible: {str(e)}")
        if settings.ENVIRONMENT == 'development':
            print("   This is normal for localhost - webhook needs ngrok or similar")
        return False

def test_sample_data_creation():
    """Test creating sample data"""
    print("\n" + "=" * 60)
    print("SAMPLE DATA CREATION TEST")
    print("=" * 60)
    
    try:
        # Create a test booking object (not saved to database)
        class TestBooking:
            def __init__(self):
                self.id = 999999
                self.invoice_number = f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                self.customer_name = "Test Customer"
                self.phone = "123-456-7890"
                self.email = "test@example.com"
                self.location = "Test Location"
                self.order_type = "rent"
                self.price = 1000.00
                self.payment_status = "pending_payment"
                self.status = "pending"
                self.return_date = datetime.now().date() + timedelta(days=30)
                self.submitted_at = datetime.now()
        
        test_booking = TestBooking()
        
        # Test Google Sheets integration
        service = get_google_sheets_service()
        if service:
            success = append_to_sheet(test_booking)
            if success:
                print("✅ Successfully added test data to Google Sheet")
                print(f"   Test invoice number: {test_booking.invoice_number}")
            else:
                print("❌ Failed to add test data to Google Sheet")
        else:
            print("⚠️  Skipping Google Sheets test - service not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 COMPREHENSIVE DUAL ENVIRONMENT TEST SUITE")
    print("Testing Django app configuration for both localhost and PythonAnywhere")
    print("Includes Google Sheets integration testing")
    
    tests = [
        ("Environment Detection", test_environment_detection),
        ("Database Connection", test_database_connection),
        ("Email Configuration", test_email_configuration),
        ("Telegram Configuration", test_telegram_configuration),
        ("Google Sheets Integration", test_google_sheets_setup),
        ("Static Files", test_static_files),
        ("Media Files", test_media_files),
        ("Webhook Accessibility", test_webhook_accessibility),
        ("Sample Data Creation", test_sample_data_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your app is ready for both environments.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the configuration.")
    
    # Environment-specific recommendations
    print("\n" + "=" * 60)
    print("ENVIRONMENT-SPECIFIC RECOMMENDATIONS")
    print("=" * 60)
    
    if settings.ENVIRONMENT == 'production':
        print("For PythonAnywhere Production:")
        print("1. ✅ Ensure you have a paid plan for outbound internet access")
        print("2. ✅ Upload credentials.json to your project root")
        print("3. ✅ Run 'python manage.py collectstatic'")
        print("4. ✅ Set up your webhook URL in Telegram Bot API")
        print("5. ✅ Test with real booking data")
        print("6. ✅ Verify Google Sheets integration is working")
    else:
        print("For Localhost Development:")
        print("1. ✅ Install all requirements: pip install -r requirements.txt")
        print("2. ✅ Place credentials.json in project root")
        print("3. ✅ Run 'python manage.py runserver'")
        print("4. ✅ Use ngrok for Telegram webhook testing")
        print("5. ✅ Test all features locally before deploying")
        print("6. ✅ Verify Google Sheets integration locally")

if __name__ == "__main__":
    main() 