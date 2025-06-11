# SL Power - Django Web Application

A modern web application built with Django for SL Power Co., Ltd. This project includes an admin dashboard, product management, services, testimonials, and contact form functionality.

## Features

- 🎨 Modern Admin Interface using Jazzmin
- 📝 Rich Text Editor (CKEditor) integration
- 📧 Email functionality with Gmail SMTP
- 🤖 Telegram Bot integration
- 📱 Responsive design
- 🔒 Secure authentication system
- 📊 Admin dashboard with customizable UI
- 📄 Static and media file handling
- 🌐 Multi-language support (English)

## Prerequisites

- Python 3.x
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd Djangoweb
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
SECRET_KEY=your-secret-key
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
Djangoweb/
├── app/                    # Main application directory
├── static/                 # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── media/                 # User-uploaded files
├── Djangoweb/            # Project configuration
│   ├── settings.py       # Project settings
│   ├── urls.py          # URL configuration
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
└── manage.py             # Django management script
```

## Configuration

### Email Settings
The project is configured to use Gmail SMTP for sending emails. Make sure to:
1. Enable 2-factor authentication in your Gmail account
2. Generate an App Password
3. Update the email settings in `settings.py`

### Telegram Bot
The project includes Telegram bot integration for notifications. Configure your bot by:
1. Creating a new bot through BotFather
2. Getting the bot token
3. Setting up the chat ID
4. Updating the settings in `settings.py`

## Development

### Running Tests
```bash
python manage.py test
```

### Static Files
```bash
python manage.py collectstatic
```

## Deployment

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Update `ALLOWED_HOSTS`
3. Configure a production-grade database
4. Set up proper static file serving
5. Use a production-grade web server (e.g., Gunicorn)
6. Set up SSL/TLS certificates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential. All rights reserved by SL Power Co., Ltd.

## Support

For support, please contact:
- Email: kohtharoth@gmail.com
- Company: SL Power Co., Ltd
