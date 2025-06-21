from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from datetime import datetime
from app.models import (
     GeneralInfo,
     Service ,
     Testimonial ,
     FrequentlyAskedQuestion,
     ContactFormlog ,
     Product,
     ProductImage,
     HeroSection,
     RentalBooking, 
     ServiceRequest,
     FAQ,
     ContactMessage,
)
from django.utils import timezone
from app.views import send_telegram_message, send_invoice_to_telegram
from app.utils import update_sheet_status, update_payment_status

@admin.register(GeneralInfo)
class GeneralInfoAdmin(admin.ModelAdmin):
  
    list_display = [
       'company_name',
       'company_logo',
       'location',
       'email',
       'phone',
       'open_hours',
    ]

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    
    list_display = [
        'title',
        'description'
    ]
    search_fields = [
        "title",
        "description"
    ]

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "user_job_title",
        "display_rating_count",
    ]
    def display_rating_count(self , obj):
        return '*' * obj.rating_count
    display_rating_count.short_description="Rating"

@admin.register(FrequentlyAskedQuestion)
class FrequentlyAskedQuestion(admin.ModelAdmin):
    list_display =[
        'question',
        'answer' ,
    ]

@admin.register(ContactFormlog)
class ContactFormlogAdmin(admin.ModelAdmin):
  
    list_display = [
       'email',
       'is_success',
       'is_error',
       'action_time',
    ]

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2  # Number of empty forms to display
    fields = ['image']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'product_image',
        'price',
        'rent_price',
        'power_output',
        'fuel_type',
        'status',
        'created_at',
    ]

    list_filter = ['status', 'fuel_type', 'free_delivery', 'technical_support']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'product_image', 'price', 'rent_price', 'status')
        }),
        ('Basic Product Specs', {
            'fields': ('power_output', 'fuel_type', 'phase', 'noise_level', 'tank_capacity', 'runtime')
        }),
        ('Service & Support', {
            'fields': ('free_delivery', 'warranty_period', 'installation_time', 'technical_support', 'replacement_guarantee')
        }),
        ('Rental Options', {
            'fields': ('rental_duration', 'maintenance_plan')
        }),
        ('Optional Add-ons', {
            'fields': ('ats_panel', 'onsite_technician', 'power_backup_design')
        }),
        ('Legacy Fields', {
            'fields': ('kva', 'country', 'kwg', 'specification'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline]

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('tag_lines', 'display_order', 'is_active')  # Columns in the admin list view
    list_editable = ('display_order', 'is_active')  # Editable fields directly in the list
    list_filter = ('is_active',)  # Filter sidebar for active/inactive
    search_fields = ('tag_lines',)  # Search by tagline
    ordering = ('display_order',)  # Default sort order

    # Optional: Customize the form layout
    fieldsets = (
        (None, {
            'fields': ('tag_lines', 'hero_img', 'video_url')
        }),
        ('Status & Order', {
            'fields': ('is_active', 'display_order'),
        }),
    )

def export_to_excel(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="rental_bookings_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    # Write headers
    writer.writerow([
        'Invoice Number',
        'Customer Name',
        'Phone',
        'Email',
        'Location',
        'Order Type',
        'Product',
        'Rental Date',
        'Return Date',
        'Price',
        'Deposit Amount',
        'Balance Amount',
        'Payment Status',
        'Status',
        'ATS Panel',
        'Onsite Technician',
        'Power Backup Design',
        'Delivery Address',
        'Notes',
        'Submitted At',
        'Updated At'
    ])
    
    # Write data
    for booking in queryset:
        writer.writerow([
            booking.invoice_number,
            booking.customer_name,
            booking.phone,
            booking.email,
            booking.location,
            booking.order_type,
            booking.product.title if booking.product else 'N/A',
            booking.rental_date,
            booking.return_date,
            booking.price,
            booking.deposit_amount,
            booking.balance_amount,
            booking.payment_status,
            booking.status,
            'Yes' if booking.ats_panel else 'No',
            'Yes' if booking.onsite_technician else 'No',
            'Yes' if booking.power_backup_design else 'No',
            booking.delivery_address,
            booking.notes,
            booking.submitted_at,
            booking.updated_at
        ])
    
    return response

export_to_excel.short_description = "Export selected bookings to Excel"

@admin.register(RentalBooking)
class RentalBookingAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'customer_name', 'phone', 'email', 'get_product_name',
        'order_type', 'price', 'payment_status', 'status', 'submitted_at',
    ]
    list_filter = [
        'status', 'payment_status', 'order_type', 'submitted_at',
        'ats_panel', 'onsite_technician', 'power_backup_design'
    ]
    search_fields = [
        'customer_name', 'phone', 'email', 'invoice_number',
        'product__title', 'delivery_address'
    ]
    readonly_fields = [
        'submitted_at', 'updated_at', 'invoice_number',
        'deposit_amount', 'balance_amount'
    ]
    actions = [export_to_excel, 'approve_orders', 'reject_orders', 'mark_as_paid', 'mark_as_pending_payment', 'mark_as_deposit_paid', 'mark_as_fully_paid']

    fieldsets = (
        ('Basic Information', {
            'fields': ('customer_name', 'phone', 'email', 'location', 'delivery_address')
        }),
        ('Order Details', {
            'fields': ('order_type', 'product', 'rental_date', 'return_date', 'notes', 'image')
        }),
        ('Financial Information', {
            'fields': ('price', 'deposit_amount', 'balance_amount', 'payment_status')
        }),
        ('Optional Services', {
            'fields': ('ats_panel', 'onsite_technician', 'power_backup_design'),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': ('status', 'rejection_reason', 'submitted_at', 'updated_at', 'invoice_number')
        }),
    )

    def get_product_name(self, obj):
        if obj.product:
            return obj.product.title
        return '-'
    get_product_name.short_description = 'Product'
    get_product_name.admin_order_field = 'product__title'

    def approve_orders(self, request, queryset):
        for order in queryset:
            if order.status == 'pending':
                order.status = 'approved'
                order.save()
                
                # Update Google Sheets
                from app.utils import update_sheet_status
                update_sheet_status(order)
                
                # Send Telegram notification
                message = f"""
✅ Order Approved!

📋 Invoice: {order.invoice_number}
👤 Customer: {order.customer_name}
📞 Phone: {order.phone}
📧 Email: {order.email}

🔌 Product: {order.product.title if order.product else 'N/A'}
💰 Total: ${order.price}
💵 Deposit (30%): ${order.deposit_amount}
💵 Balance: ${order.balance_amount}

📍 Delivery: {order.delivery_address}
📝 Notes: {order.notes or 'None'}

🕒 Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                send_telegram_message(message)
                # Send PDF invoice to Telegram
                send_invoice_to_telegram(order)
        self.message_user(request, f"{queryset.count()} orders were successfully approved.")
    approve_orders.short_description = "Approve selected orders"

    def reject_orders(self, request, queryset):
        for order in queryset:
            if order.status == 'pending':
                order.status = 'rejected'
                order.save()
                
                # Update Google Sheets
                from app.utils import update_sheet_status
                update_sheet_status(order)
                
                # Send Telegram notification
                message = f"""
❌ Order Rejected!

👤 Customer: {order.customer_name}
📞 Phone: {order.phone}
📧 Email: {order.email}

🔌 Product: {order.product.title if order.product else 'N/A'}
💰 Total: ${order.price}

🕒 Rejected: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                send_telegram_message(message)
                
        self.message_user(request, f"{queryset.count()} orders were successfully rejected.")
    reject_orders.short_description = "Reject selected orders"

    def mark_as_paid(self, request, queryset):
        for order in queryset:
            order.payment_status = 'paid'
            order.save()
            
            # Update Google Sheets
            update_payment_status(order)
            
            # Send Telegram notification
            message = f"""
💰 Payment Received!

📋 Invoice: {order.invoice_number}
👤 Customer: {order.customer_name}
📞 Phone: {order.phone}
📧 Email: {order.email}

🔌 Product: {order.product.title if order.product else 'N/A'}
💰 Total: ${order.price}
💵 Amount Paid: ${order.price}

🕒 Payment Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
            send_telegram_message(message)
            
        self.message_user(request, f"{queryset.count()} orders were marked as paid.")
    mark_as_paid.short_description = "Mark selected orders as paid"

    def mark_as_pending_payment(self, request, queryset):
        for order in queryset:
            order.payment_status = 'pending_payment'
            order.save()
            
            # Update Google Sheets
            update_payment_status(order)
            
            # Send Telegram notification
            message = f"""
⏳ Payment Pending!

📋 Invoice: {order.invoice_number}
👤 Customer: {order.customer_name}
📞 Phone: {order.phone}
📧 Email: {order.email}

🔌 Product: {order.product.title if order.product else 'N/A'}
💰 Total: ${order.price}
💵 Deposit (30%): ${order.deposit_amount}
💳 Balance: ${order.balance_amount}

🕒 Status Updated: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
            send_telegram_message(message)
            
        self.message_user(request, f"{queryset.count()} orders were marked as pending payment.")
    mark_as_pending_payment.short_description = "Mark selected orders as pending payment"

    def mark_as_deposit_paid(self, request, queryset):
        for order in queryset:
            order.payment_status = 'deposit_paid'
            order.save()
            
            # Update Google Sheets
            update_payment_status(order)
            
            # Send Telegram notification
            message = f"""
💰 Deposit Paid!

📋 Invoice: {order.invoice_number}
👤 Customer: {order.customer_name}
📞 Phone: {order.phone}
📧 Email: {order.email}

🔌 Product: {order.product.title if order.product else 'N/A'}
💰 Total: ${order.price}
💵 Deposit (30%): ${order.deposit_amount}
💵 Balance: ${order.balance_amount}

🕒 Deposit Paid: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
            send_telegram_message(message)
            
        self.message_user(request, f"{queryset.count()} orders were marked as deposit paid.")
    mark_as_deposit_paid.short_description = "Mark selected orders as deposit paid"

    def mark_as_fully_paid(self, request, queryset):
        for order in queryset:
            order.payment_status = 'fully_paid'
            order.save()
            
            # Update Google Sheets
            update_payment_status(order)
            
            # Send Telegram notification
            message = f"""
💰 Fully Paid!

📋 Invoice: {order.invoice_number}
👤 Customer: {order.customer_name}
📞 Phone: {order.phone}
📧 Email: {order.email}

🔌 Product: {order.product.title if order.product else 'N/A'}
💰 Total: ${order.price}
💵 Amount Paid: ${order.price}

🕒 Payment Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
            send_telegram_message(message)
            
        self.message_user(request, f"{queryset.count()} orders were marked as fully paid.")
    mark_as_fully_paid.short_description = "Mark selected orders as fully paid"

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name',
        'machine_type',
        'issue_description_short',
        'preferred_date',
        'submitted_at',
        'status',
    ]
    search_fields = ['customer_name', 'machine_type', 'issue_description']
    list_filter = ['preferred_date', 'status']
    ordering = ['-submitted_at']
    readonly_fields = ['customer_name', 'phone', 'issue_description', 'submitted_at', 'image']

    def issue_description_short(self, obj):
        return obj.issue_description[:40] + '...' if len(obj.issue_description) > 40 else obj.issue_description
    issue_description_short.short_description = "Issue"

    def status_colored(self, obj):
        color = {
            'Pending': 'orange',
            'In Progress': 'blue',
            'Resolved': 'green',
        }.get(obj.status, 'gray')
        return format_html('<b style="color:{};">{}</b>', color, obj.status)
    status_colored.short_description = 'Status'
    status_colored.admin_order_field = 'status'  # enables sorting by status

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')
    ordering = ('category', 'created_at')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False  # Disable adding new messages from admin
    
    def has_change_permission(self, request, obj=None):
        return True  # Allow editing (marking as read)
    
    def has_delete_permission(self, request, obj=None):
        return True  # Allow deleting messages
    