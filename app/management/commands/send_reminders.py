from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from app.models import RentalBooking, ServiceRequest, GeneralInfo
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from app.views import send_telegram_message

class Command(BaseCommand):
    help = 'Sends reminders for rental returns and service appointments that are due soon.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting the reminder job...'))

        # Define the reminder period (e.g., 3 days from now)
        reminder_date = timezone.now().date() + timedelta(days=3)

        # Get company info for emails
        general_info = GeneralInfo.objects.first()
        if not general_info:
            self.stdout.write(self.style.ERROR('GeneralInfo not found. Cannot send reminders.'))
            return

        # Process rental return reminders
        self.send_rental_reminders(reminder_date, general_info)

        # Process service appointment reminders
        self.send_service_reminders(reminder_date, general_info)

        self.stdout.write(self.style.SUCCESS('Reminder job finished.'))

    def send_rental_reminders(self, reminder_date, general_info):
        """Sends reminders for upcoming rental returns."""
        upcoming_returns = RentalBooking.objects.filter(
            return_date=reminder_date,
            status='approved',
            reminder_sent=False
        )

        if not upcoming_returns.exists():
            self.stdout.write(self.style.NOTICE('No upcoming rental returns to remind.'))
            return

        self.stdout.write(f'Found {upcoming_returns.count()} upcoming rental returns.')

        for booking in upcoming_returns:
            # Send email to customer
            self.send_customer_rental_reminder(booking, general_info)
            
            # Send notification to admin
            self.send_admin_rental_reminder(booking)

            # Mark as reminder sent
            booking.reminder_sent = True
            booking.save()

    def send_service_reminders(self, reminder_date, general_info):
        """Sends reminders for upcoming service appointments."""
        upcoming_services = ServiceRequest.objects.filter(
            preferred_date=reminder_date,
            status='in_progress',
            reminder_sent=False
        )

        if not upcoming_services.exists():
            self.stdout.write(self.style.NOTICE('No upcoming service appointments to remind.'))
            return

        self.stdout.write(f'Found {upcoming_services.count()} upcoming service appointments.')

        for service in upcoming_services:
            # Send email to customer
            self.send_customer_service_reminder(service, general_info)

            # Send notification to admin
            self.send_admin_service_reminder(service)

            # Mark as reminder sent
            service.reminder_sent = True
            service.save()

    def send_customer_rental_reminder(self, booking, general_info):
        """Sends a rental return reminder email to the customer."""
        if not booking.email:
            return

        subject = f"Reminder: Your Rental Return for {booking.product.title} is Due Soon"
        context = {
            'booking': booking,
            'general_info': general_info,
            'reminder_type': 'rental_customer',
        }
        html_message = render_to_string('reminders/reminder.html', context)
        
        try:
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [booking.email], html_message=html_message)
            self.stdout.write(self.style.SUCCESS(f'Sent rental reminder to customer: {booking.customer_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send rental reminder to {booking.email}: {e}'))

    def send_admin_rental_reminder(self, booking):
        """Sends a rental return reminder to the admin via Telegram and email."""
        # Telegram notification
        telegram_message = f"""
        🔔 *Upcoming Rental Return Reminder* 🔔
        
        *Customer:* {booking.customer_name}
        *Product:* {booking.product.title}
        *Return Date:* {booking.return_date.strftime('%Y-%m-%d')}
        
        Please prepare for the return and follow up if needed.
        """
        send_telegram_message(telegram_message.strip())

        # Email notification to admin
        subject = f"Upcoming Rental Return: {booking.customer_name} - {booking.product.title}"
        context = {
            'booking': booking,
            'reminder_type': 'rental_admin',
        }
        html_message = render_to_string('reminders/reminder.html', context)
        
        try:
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], html_message=html_message)
            self.stdout.write(self.style.SUCCESS('Sent rental reminder to admin email.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send admin rental reminder email: {e}'))

    def send_customer_service_reminder(self, service, general_info):
        """Sends a service appointment reminder email to the customer."""
        if not service.email:
            return

        subject = f"Reminder: Your Service Appointment for {service.machine_type}"
        context = {
            'service': service,
            'general_info': general_info,
            'reminder_type': 'service_customer',
        }
        html_message = render_to_string('reminders/reminder.html', context)

        try:
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [service.email], html_message=html_message)
            self.stdout.write(self.style.SUCCESS(f'Sent service reminder to customer: {service.customer_name}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send service reminder to {service.email}: {e}'))

    def send_admin_service_reminder(self, service):
        """Sends a service appointment reminder to the admin via Telegram and email."""
        # Telegram notification
        telegram_message = f"""
        🔔 *Upcoming Service Appointment Reminder* 🔔
        
        *Customer:* {service.customer_name}
        *Service:* {service.service_type} for {service.machine_type}
        *Appointment Date:* {service.preferred_date.strftime('%Y-%m-%d')}
        
        Please ensure staff and resources are ready.
        """
        send_telegram_message(telegram_message.strip())

        # Email notification to admin
        subject = f"Upcoming Service: {service.customer_name} - {service.service_type}"
        context = {
            'service': service,
            'reminder_type': 'service_admin',
        }
        html_message = render_to_string('reminders/reminder.html', context)
        
        try:
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], html_message=html_message)
            self.stdout.write(self.style.SUCCESS('Sent service reminder to admin email.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send admin service reminder email: {e}')) 