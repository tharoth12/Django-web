# SL Power Django Web Application

A comprehensive Django web application for SL Power, featuring rental booking, service requests, Google Sheets integration, Telegram notifications, and email functionality.

## 🚀 Features

- **Rental & Purchase Booking System**: Complete booking management with invoice generation
- **Service Request Management**: Customer service requests with priority levels
- **Google Sheets Integration**: Automatic data sync to Google Sheets
- **Telegram Bot Integration**: Real-time notifications and approval system
- **Email Notifications**: Automated email sending for bookings and approvals
- **Admin Dashboard**: Comprehensive admin interface with Jazzmin
- **Responsive Design**: Modern, mobile-friendly UI
- **Dual Environment Support**: Works on both localhost and PythonAnywhere

## 🛠️ Technology Stack

- **Backend**: Django 5.0+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **PDF Generation**: WeasyPrint
- **Admin Interface**: Django Jazzmin
- **External APIs**: Google Sheets API, Telegram Bot API
- **Email**: Gmail SMTP

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Google Sheets API enabled
- Telegram Bot Token
- Gmail App Password
- PythonAnywhere account (for production deployment)

## 🏠 Quick Start (Localhost)

### 1. Clone and Setup
```bash
git clone https://github.com/tharoth12/Django-web
cd "Django web"

# Run the automated setup script
python setup.py
```

### 2. Manual Setup (if needed)
```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### 3. Configure Environment
1. Edit `myenv/tokenemailandtelegram.txt` with your credentials:
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
GOOGLE_SHEET_ID=your_sheet_id
```

2. Download Google Sheets credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Google Sheets API
   - Create a service account
   - Download `credentials.json`
   - Place it in the project root

3. Share your Google Sheet with the service account email

### 4. Test and Run
```bash
# Run comprehensive tests
python test_dual_environment.py

# Start development server
python manage.py runserver

# Visit http://localhost:8000
```

## ☁️ Production Deployment (PythonAnywhere)

### 1. Upload Code
1. Go to PythonAnywhere Files tab
2. Upload your project to `/home/yourusername/Django web/`

### 2. Setup Environment
```bash
# In PythonAnywhere console
cd "/home/yourusername/Django web"

# Create virtual environment
python3.10 -m venv myenv

# Activate and install dependencies
source myenv/bin/activate
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py collectstatic
```

### 3. Configure Web App
1. Go to Web tab
2. Add new web app with manual configuration
3. Set source code to `/home/yourusername/Django web`
4. Configure WSGI file (see deployment guide)

### 4. Upload Credentials
1. Upload `credentials.json` to project root
2. Edit `myenv/tokenemailandtelegram.txt` with production credentials

### 5. Test and Deploy
```bash
# Run tests
python test_dual_environment.py

# Reload web app
# Visit https://yourusername.pythonanywhere.com
```

## 🧪 Testing

### Comprehensive Test Suite
```bash
python test_dual_environment.py
```

This tests:
- Environment detection
- Database connection
- Email configuration
- Telegram configuration
- Google Sheets integration
- Static files
- Media files
- Webhook accessibility
- Sample data creation

### Individual Tests
```bash
# Test specific functionality
python manage.py test app

# Check deployment settings
python manage.py check --deploy
```

## 📁 Project Structure

```
Django web/
├── app/                    # Main Django application
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── admin.py           # Admin interface
│   ├── utils.py           # Google Sheets utilities
│   └── signals.py         # Django signals
├── Djangoweb/             # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI configuration
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── media/                 # User uploaded files
├── myenv/                 # Virtual environment
│   └── tokenemailandtelegram.txt  # Environment variables
├── credentials.json       # Google Sheets credentials
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
├── setup.py              # Automated setup script
├── test_dual_environment.py  # Comprehensive test suite
├── DUAL_ENVIRONMENT_DEPLOYMENT.md  # Detailed deployment guide
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables
The app uses the following environment variables (set in `myenv/tokenemailandtelegram.txt`):

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TELEGRAM_CHAT_ID`: Your Telegram chat ID
- `EMAIL_HOST_USER`: Gmail address
- `EMAIL_HOST_PASSWORD`: Gmail app password
- `GOOGLE_SHEET_ID`: Your Google Sheet ID

### Google Sheets Setup
1. Create a Google Cloud Project
2. Enable Google Sheets API
3. Create a service account
4. Download credentials.json
5. Share your Google Sheet with the service account email

### Telegram Bot Setup
1. Create a bot with @BotFather
2. Get your bot token
3. Get your chat ID
4. Set up webhook (for production)

## 🚀 Features in Detail

### Booking System
- Rental and purchase bookings
- Optional services (ATS Panel, Onsite Technician, etc.)
- Automatic invoice generation
- Payment status tracking
- Email notifications

### Service Requests
- Multiple service types
- Priority levels
- Onsite technician options
- Image upload support
- Status tracking

### Admin Interface
- Jazzmin admin theme
- Bulk actions for bookings
- Export to Excel
- Status management
- Payment tracking

### Integration Features
- **Google Sheets**: Real-time data sync
- **Telegram**: Instant notifications and approvals
- **Email**: Automated customer communications
- **PDF Generation**: Professional invoices

## 🔐 Security

### Development (Localhost)
- Debug mode enabled
- Less strict security settings
- For development and testing only

### Production (PythonAnywhere)
- Debug mode disabled
- SSL/HTTPS enforced
- Strict security headers
- Environment-specific settings

### Credentials Security
- Never commit `credentials.json` to version control
- Keep environment files secure
- Use environment variables for sensitive data
- Regularly rotate service account keys

## 🐛 Troubleshooting

### Common Issues

#### Localhost
- **Port in use**: Use `python manage.py runserver 8001`
- **Static files not loading**: Run `python manage.py collectstatic`
- **Database errors**: Run `python manage.py migrate`

#### PythonAnywhere
- **Import errors**: Check virtual environment activation
- **Static files 404**: Run `python manage.py collectstatic`
- **Google Sheets not working**: Check paid plan and credentials
- **Webhook not working**: Check webhook URL and bot token

#### Google Sheets
- **Credentials not found**: Upload credentials.json to project root
- **Access denied**: Share Google Sheet with service account email
- **Invalid sheet ID**: Check GOOGLE_SHEET_ID in environment variables

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

# Run comprehensive tests
python test_dual_environment.py
```

## 📞 Support

If you encounter issues:

1. **Run the test suite**: `python test_dual_environment.py`
2. **Check error logs**: Review PythonAnywhere error logs
3. **Verify configuration**: Follow the deployment guide
4. **Test features individually**: Isolate the problem
5. **Check environment requirements**: Ensure all prerequisites are met

## 📚 Documentation

- [Dual Environment Deployment Guide](DUAL_ENVIRONMENT_DEPLOYMENT.md) - Detailed setup instructions
- [Django Documentation](https://docs.djangoproject.com/) - Django framework docs
- [Google Sheets API](https://developers.google.com/sheets/api) - Google Sheets integration
- [Telegram Bot API](https://core.telegram.org/bots/api) - Telegram bot documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software for SL Power.

---

**Note**: This application requires a PythonAnywhere paid plan for Google Sheets integration due to outbound internet access requirements.
