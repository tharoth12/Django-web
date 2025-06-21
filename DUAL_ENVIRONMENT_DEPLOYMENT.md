# Dual Environment Deployment Guide

This guide helps you deploy your Django app on both localhost (development) and PythonAnywhere (production), including Google Sheets integration.

## 🏠 Localhost Development Setup

### Prerequisites
- Python 3.8+ installed
- Git installed
- Virtual environment tool (venv or virtualenv)

### Step 1: Clone and Setup
```bash
# Clone your repository
git clone <your-repo-url>
cd "Django web"

# Create virtual environment
python -m venv myenv

# Activate virtual environment
# On Windows:
myenv\Scripts\activate
# On macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Environment Configuration
```bash
# Create environment file
cp myenv/tokenemailandtelegram.txt myenv/tokenemailandtelegram.txt.backup

# Edit the file with your credentials
# Make sure GOOGLE_SHEET_ID is set correctly
```

### Step 3: Google Sheets Setup
1. **Create Google Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable Google Sheets API
   - Go to "IAM & Admin" > "Service Accounts"
   - Create a service account named `django-sheets-integration`
   - Grant it "Editor" role
   - Create and download JSON key as `credentials.json`

2. **Place credentials file**:
   - Put `credentials.json` in the project root: `Django web/credentials.json`

3. **Share Google Sheet**:
   - Open your Google Sheet
   - Share it with the service account email (found in `credentials.json`)
   - Give it "Editor" permissions

### Step 4: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (if any)
python manage.py loaddata initial_data.json
```

### Step 5: Test the Setup
```bash
# Run the comprehensive test
python test_dual_environment.py

# Start development server
python manage.py runserver

# Visit http://localhost:8000
```

### Step 6: Telegram Webhook (Optional)
For testing Telegram webhooks locally:
```bash
# Install ngrok
# Download from https://ngrok.com/

# Start ngrok tunnel
ngrok http 8000

# Use the ngrok URL for your webhook
# Example: https://abc123.ngrok-free.app/telegram/webhook/
```

## ☁️ PythonAnywhere Production Setup

### Prerequisites
- PythonAnywhere paid account (for outbound internet access)
- Google Cloud Project with Google Sheets API enabled

### Step 1: Upload Your Code
1. Go to PythonAnywhere Files tab
2. Navigate to `/home/yourusername/`
3. Upload your entire project folder
4. Rename to `Django web` if needed

### Step 2: Setup Virtual Environment
```bash
# In PythonAnywhere console
cd "/home/yourusername/Django web"

# Create virtual environment
python3.10 -m venv myenv

# Activate virtual environment
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Environment Configuration
1. Go to Files tab
2. Navigate to `/home/yourusername/Django web/myenv/`
3. Edit `tokenemailandtelegram.txt` with your production credentials
4. Make sure `GOOGLE_SHEET_ID` is correct

### Step 4: Google Sheets Setup
1. **Upload credentials file**:
   - Upload `credentials.json` to `/home/yourusername/Django web/credentials.json`
   - Make sure the file has correct permissions

2. **Verify sheet sharing**:
   - Ensure your Google Sheet is shared with the service account email
   - The service account should have "Editor" permissions

### Step 5: Database Setup
```bash
# In PythonAnywhere console
cd "/home/yourusername/Django web"
source myenv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Step 6: Configure Web App
1. Go to PythonAnywhere Web tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Choose Python 3.10
5. Set source code to: `/home/yourusername/Django web`
6. Set working directory to: `/home/yourusername/Django web`

### Step 7: Configure WSGI File
Edit the WSGI file:
```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/Django web'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'Djangoweb.settings'
os.environ['DJANGO_ENVIRONMENT'] = 'production'

# Activate virtual environment
activate_this = '/home/yourusername/Django web/myenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Step 8: Test the Setup
```bash
# In PythonAnywhere console
cd "/home/yourusername/Django web"
source myenv/bin/activate

# Run the comprehensive test
python test_dual_environment.py
```

### Step 9: Reload Web App
1. Go to Web tab
2. Click "Reload" on your web app
3. Visit your site: `https://yourusername.pythonanywhere.com`

### Step 10: Setup Telegram Webhook
```bash
# Get your webhook URL
WEBHOOK_URL="https://yourusername.pythonanywhere.com/telegram/webhook/"

# Set webhook via Telegram API
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"$WEBHOOK_URL\"}"
```

## 🔄 Environment Switching

### Automatic Detection
The app automatically detects the environment:
- **Localhost**: Development mode with debug enabled
- **PythonAnywhere**: Production mode with security settings

### Manual Override
You can manually set the environment:
```bash
# For development
export DJANGO_ENVIRONMENT=development

# For production
export DJANGO_ENVIRONMENT=production
```

## 🧪 Testing Both Environments

### Run Comprehensive Tests
```bash
# This tests all functionality on both environments
python test_dual_environment.py
```

### Test Specific Features
```bash
# Test local development
python manage.py runserver
# Then visit http://localhost:8000
```

## 🔧 Troubleshooting

### Common Localhost Issues
1. **Port already in use**: Change port with `python manage.py runserver 8001`
2. **Static files not loading**: Run `python manage.py collectstatic`
3. **Database errors**: Run `python manage.py migrate`
4. **Google Sheets not working**: Check credentials.json location and sheet sharing

### Common PythonAnywhere Issues
1. **Import errors**: Check virtual environment activation
2. **Static files 404**: Run `python manage.py collectstatic`
3. **Google Sheets not working**: Check paid plan and credentials
4. **Webhook not working**: Check webhook URL and bot token

### Google Sheets Specific Issues
1. **"Credentials file not found"**: Upload credentials.json to project root
2. **"Service account has no access"**: Share Google Sheet with service account email
3. **"Invalid sheet ID"**: Check GOOGLE_SHEET_ID in environment variables
4. **"Outbound internet access not allowed"**: Upgrade to PythonAnywhere paid plan

### Debug Commands
```bash
# Check environment
echo $DJANGO_ENVIRONMENT

# Check Python path
python -c "import sys; print(sys.path)"

# Check installed packages
pip list

# Check Django settings
python manage.py check --deploy

# Test Google Sheets specifically
python test_dual_environment.py
```

## 📁 File Structure
```
Django web/
├── app/                    # Django app
├── Djangoweb/             # Django project
├── static/                # Static files
├── templates/             # HTML templates
├── media/                 # User uploads
├── myenv/                 # Virtual environment
│   └── tokenemailandtelegram.txt  # Environment variables
├── credentials.json       # Google Sheets credentials
├── requirements.txt       # Python dependencies
├── manage.py             # Django management
├── test_dual_environment.py  # Comprehensive test script
└── README.md             # Project documentation
```

## 🔐 Security Notes

### Localhost
- Debug mode enabled for development
- Less strict security settings
- Use for development and testing only

### PythonAnywhere
- Debug mode disabled
- SSL/HTTPS enforced
- Strict security headers
- Use for production

### Credentials
- Never commit `credentials.json` to version control
- Keep `tokenemailandtelegram.txt` secure
- Use environment variables for sensitive data
- Regularly rotate service account keys

## 🚀 Deployment Checklist

### Before Deploying to Production
- [ ] All tests pass locally (`python test_dual_environment.py`)
- [ ] Google Sheets integration working
- [ ] Email configuration tested
- [ ] Telegram bot responding
- [ ] Static files collected
- [ ] Database migrated
- [ ] Environment variables set
- [ ] Credentials uploaded
- [ ] Google Sheet shared with service account

### After Deploying to Production
- [ ] Web app loads without errors
- [ ] Admin panel accessible
- [ ] Booking form works
- [ ] Google Sheets syncs data
- [ ] Telegram notifications sent
- [ ] Email notifications sent
- [ ] Webhook responds correctly
- [ ] SSL certificate working
- [ ] All tests pass on production

## 📞 Support

If you encounter issues:
1. Check the test output: `python test_dual_environment.py`
2. Review error logs in PythonAnywhere
3. Verify all configuration steps
4. Test features one by one
5. Check environment-specific requirements
6. Verify Google Sheets setup and permissions 