from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RentalBooking
from .utils import update_payment_status, update_sheet_status

@receiver(post_save, sender=RentalBooking)
def update_google_sheets_on_booking_change(sender, instance, created, **kwargs):
    """
    Automatically update Google Sheets when booking status or payment status changes
    """
    if not created:  # Only for updates, not new records
        try:
            print(f"Updating Google Sheets for invoice {instance.invoice_number}")
            # Update both status and payment status
            update_sheet_status(instance)
        except Exception as e:
            print(f"Error updating Google Sheets: {str(e)}") 