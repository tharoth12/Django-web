# -*- coding: utf-8 -*-
from django.shortcuts import render , redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator , PageNotAnInteger , EmptyPage
from django.http import HttpResponse
import requests
import json
from datetime import datetime, timedelta
import tempfile
import os
from app.models import ( 
   GeneralInfo ,
   Service ,
   Testimonial,
   FrequentlyAskedQuestion,
   ContactFormlog,
   Product,
   HeroSection,
   RentalBooking,
   ServiceRequest,
)
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.urls import reverse
from django.http import JsonResponse
from .utils import append_to_sheet

# Create your views here.
def index (request):

   general_info = GeneralInfo.objects.first()

   services = Service.objects.all()

   testimonials = Testimonial.objects.all()

   faqs= FrequentlyAskedQuestion.objects.all()

   hero_sections = HeroSection.objects.filter(is_active=True).order_by('display_order')

   recent_products = Product.objects.all().order_by("-created_at")[:6]
   
   # serviceRequest = ServiceRequest.objects.all().order_by("-created_at")[:6]
   
   rental_booking = RentalBooking.objects.all()

   for product in recent_products:  
    print(f"product : {product}")
    print(f"product.created_at : {product.created_at}")
    print(f"Product name: {product.title}")
    print("")

   default_value = ""
   context = {
      "company_logo":getattr(general_info, "company_logo", default_value),
      "company_name":getattr(general_info, "company_name", default_value),
      "location":getattr(general_info, "location" , default_value),
      "email":getattr(general_info, "email", default_value),
      "phone":getattr(general_info , "phone",  default_value),
      "open_hours":getattr(general_info, "open_hours" , default_value),
      "video_url":getattr(general_info, "video_url" , default_value),
      "telegram_url":getattr (general_info, "Telegram_url", default_value),
      "facebook_url":getattr (general_info, "Facebook_url", default_value),
      "services":services,
      "testimonials" :testimonials,
      "faqs" : faqs,
      "recent_products": recent_products,
      "hero_sections" : hero_sections,
      "rental_booking": rental_booking,
      # "service_request": serviceRequest,
   }

   return render(request, "index.html" , context)
   
def contact_form(request):
   if request.method == 'POST':
      print("\nUser has submit a contact form\n")
      name = request.POST.get('name')
      email = request.POST.get('email')
      subject = request.POST.get ('subject')
      message = request.POST.get ('message')

      context = {
         "name":name,
         "email":email,
         "subject": subject,
         "message": message,
      }
      html_content  = render_to_string('email.html', context)

      is_success = False
      is_error = False
      error_message = ""
      
      try:
         send_mail(
            subject=subject,
            message=None,
            html_message=html_content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently= False,
         )
      except Exception as e:
         is_error = True
         error_message = str(e)
         messages.error(request, "There is an error , cound not send email")
      else :
         is_success = True

         messages.success(request, "Email has been sent")

      ContactFormlog.objects.create (
         name = name,
         email = email,
         subject = subject,
         action_time = timezone.now(),
         is_success = is_success,
         is_error = is_error,
         error_message = error_message,

      )

   return redirect('home') 

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Get 3 recent products excluding the current product
    recent_products = Product.objects.exclude(id=product_id).order_by('-created_at')[:3]
    context = {
        'product': product,
        'recent_products': recent_products,
    }
    return render(request, 'product_details.html', context)

def products(request):
      
      all_products = Product.objects.all().order_by("-created_at")
      product_per_page = 9
      paginator = Paginator(all_products, product_per_page)

      print(f"paginator.num_pages:{paginator.num_pages}")

      page = request.GET.get('page')

      print(f"page :{page}")

      try:
         products = paginator.page(page)  
      except PageNotAnInteger:
         products = paginator.page(1)
      except EmptyPage:
         products = paginator.page(paginator.num_pages)

      context ={
         "products": products,
      }
      return render(request, "products.html", context )

def hero_section(request):
   hero_sections = HeroSection.objects.filter(is_active=True).order_by('display_order')
   
   context ={
      'hero_sections':hero_sections,
   }
   return render(request , 'hero.html', {'hero_sections': hero_sections} , context)

def send_telegram_message(message, booking=None, keyboard=None):
    try:
        TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
        TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID
        
        if booking:
            message = f"""
New {booking.order_type.title()} Request

Customer: {booking.customer_name}
Phone: {booking.phone}
Email: {booking.email}
Location: {booking.location}

Order Details:
"""
            # Add optional services if any
            optional_services = []
            if booking.ats_panel:
                optional_services.append("ATS Panel ($300)")
            if booking.onsite_technician:
                optional_services.append("Onsite Technician ($100)")
            if booking.power_backup_design:
                optional_services.append("Power Backup Design ($50)")

            # Calculate subtotal (price minus optional services)
            message += f"{'Rent Subtotal' if booking.order_type == 'rent' else 'Purchase Price'}: ${booking.price - booking.get_total_optional_services():,.2f}\n"
            
            if optional_services:
                message += "\nOptional Services:\n"
                for service in optional_services:
                    message += f"{service}\n"
            
            message += f"\nProduct: {booking.product.title}\n"
            
            if booking.order_type == 'rent':
                message += f"Rent: ${booking.product.rent_price}/month | Full Price: ${booking.product.price}\n"
            
            message += f"\nNotes: {booking.notes or 'None'}\n"
            
            message += f"\n\nSubmitted: {booking.submitted_at.strftime('%Y-%m-%d %H:%M')}\n"
            
            if not keyboard:
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "Approve", "callback_data": f"approve_{booking.id}"},
                            {"text": "Reject", "callback_data": f"reject_{booking.id}"}
                        ]
                    ]
                }
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        if keyboard:
            data["reply_markup"] = json.dumps(keyboard)
        
        response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        print(f"Error sending telegram message: {str(e)}")
        return None

def generate_invoice(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    general_info = GeneralInfo.objects.first()
    qr_code_url = request.build_absolute_uri(static('assets/img/QR.jpg'))
    
    # Calculate rental months if it's a rental order
    months = None
    if booking.order_type == 'rent' and booking.rental_date and booking.return_date:
        months = (booking.return_date.year - booking.rental_date.year) * 12 + (booking.return_date.month - booking.rental_date.month)
        if booking.return_date.day > booking.rental_date.day:
            months += 1
        months = max(1, months)  # Ensure at least 1 month
    
    context = {
        'booking': booking,
        'general_info': general_info,
        'BASE_DIR': settings.BASE_DIR,  # For font path in template
        'qr_code_url': qr_code_url,     # Absolute URL for QR code
        'months': months,               # Add months to context
    }
    html_string = render_to_string('invoice.html', context)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf(tmp_file)
        tmp_file_path = tmp_file.name
    response = HttpResponse(open(tmp_file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="invoice_{booking.invoice_number}.pdf"'
    return response

def rental_booking(request):
    # Get the type and product_id from the URL parameters
    action_type = request.GET.get('type', 'rent')  # Default to 'rent' if not specified
    product_id = request.GET.get('product_id')
    
    # Get the product if product_id is provided
    product = None
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found.")
            return redirect('home')

    if request.method == 'POST':
        print("\nUser has submitted a rental booking form\n")
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        
        # Get form data
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        location = request.POST.get('location')
        rental_date = request.POST.get('rental_date')
        rental_period = request.POST.get('rental_period')
        notes = request.POST.get('notes')
        delivery_address = request.POST.get('delivery_address')
        image = request.FILES.get('image')

        print("\nForm data received:")
        print(f"customer_name: {customer_name}")
        print(f"phone: {phone}")
        print(f"email: {email}")
        print(f"location: {location}")
        print(f"rental_date: {rental_date}")
        print(f"rental_period: {rental_period}")
        print(f"notes: {notes}")
        print(f"delivery_address: {delivery_address}")
        print(f"image: {image}")

        # Get optional services
        ats_panel = request.POST.get('ats_panel') == 'on'
        onsite_technician = request.POST.get('onsite_technician') == 'on'
        power_backup_design = request.POST.get('power_backup_design') == 'on'
        maintenance_plan = request.POST.get('maintenance_plan') == 'on'

        print("\nOptional services:")
        print(f"ats_panel: {ats_panel}")
        print(f"onsite_technician: {onsite_technician}")
        print(f"power_backup_design: {power_backup_design}")
        print(f"maintenance_plan: {maintenance_plan}")

        # Convert rental_date to date object if it's a string
        if isinstance(rental_date, str) and rental_date:
            rental_date = datetime.strptime(rental_date, '%Y-%m-%d').date()
            
        # Calculate return date based on rental period
        return_date = None
        if rental_date and rental_period:
            months = int(rental_period)
            return_date = rental_date + timedelta(days=30 * months)

        # Calculate optional service costs
        ATS_COST = Decimal('300.00')
        TECH_COST = Decimal('100.00')
        BACKUP_COST = Decimal('50.00')
        MAINTENANCE_COST = Decimal('150.00')
        optional_total = Decimal('0.00')
        optional_services_list = []
        
        if ats_panel:
            optional_total += ATS_COST
            optional_services_list.append(f'ATS Panel (${ATS_COST})')
        if onsite_technician:
            optional_total += TECH_COST
            optional_services_list.append(f'Onsite Technician (${TECH_COST})')
        if power_backup_design:
            optional_total += BACKUP_COST
            optional_services_list.append(f'Power Backup Design (${BACKUP_COST})')
        if maintenance_plan:
            optional_total += MAINTENANCE_COST * Decimal(rental_period or '1')
            optional_services_list.append(f'Maintenance Plan (${MAINTENANCE_COST}/month)')

        # Calculate rent subtotal and total
        rent_subtotal = Decimal('0.00')
        months = int(rental_period or '1')
        
        if product and action_type == 'rent':
            rent_subtotal = Decimal(str(product.rent_price or 0)) * Decimal(str(months))
        elif product and action_type == 'buy':
            rent_subtotal = Decimal(str(product.price or 0))
            
        total_amount = rent_subtotal + optional_total

        try:
            # Create booking
            if product:
                print("\nCreating booking with data:")
                print(f"customer_name: {customer_name}")
                print(f"phone: {phone}")
                print(f"email: {email}")
                print(f"location: {location}")
                print(f"order_type: {action_type}")
                print(f"rental_date: {rental_date}")
                print(f"return_date: {return_date}")
                print(f"notes: {notes}")
                print(f"delivery_address: {delivery_address}")
                print(f"ats_panel: {ats_panel}")
                print(f"onsite_technician: {onsite_technician}")
                print(f"power_backup_design: {power_backup_design}")
                print(f"product: {product}")
                print(f"price: {total_amount}")
                
                booking = RentalBooking.objects.create(
                    customer_name=customer_name,
                    phone=phone,
                    email=email,
                    location=location,
                    order_type=action_type,
                    rental_date=rental_date,
                    return_date=return_date,
                    notes=notes,
                    delivery_address=delivery_address,
                    ats_panel=ats_panel,
                    onsite_technician=onsite_technician,
                    power_backup_design=power_backup_design,
                    product=product,
                    price=total_amount,
                    submitted_at=timezone.now(),
                    status='pending'
                )
                
                if image:
                    booking.image = image
                    booking.save()

                # Prepare Telegram message
                telegram_message = f"""
🔔 New {'Rental' if action_type == 'rent' else 'Purchase'} Request!

👤 Customer: {customer_name}
📞 Phone: {phone}
📧 Email: {email}
📍 Location: {location}
"""
                if action_type == 'rent':
                    telegram_message += f"📅 Period: {rental_period} months\n"
                    telegram_message += f"📅 Start Date: {rental_date}\n"
                    telegram_message += f"📅 Return Date: {return_date}\n"
                telegram_message += f"""
💼 Product: {product.title}
💰 Total Amount: ${total_amount}

Optional Services:
{chr(10).join(optional_services_list) if optional_services_list else 'None'}

📝 Notes: {notes or 'None'}
"""
                # Add keyboard buttons for approval/rejection
                keyboard = {
                    "inline_keyboard": [
                        [
                            {"text": "✅ Approve", "callback_data": f"approve_{booking.id}"},
                            {"text": "❌ Reject", "callback_data": f"reject_{booking.id}"}
                        ],
                        [
                            {"text": "🧾 Print Invoice", "callback_data": f"invoice_{booking.id}"}
                        ]
                    ]
                }
                
                # Send to Telegram with keyboard
                send_telegram_message(telegram_message, keyboard=keyboard)
                
                # Send to Google Sheets
                append_to_sheet(booking)
                
                # Success message removed; handled by success page
                return redirect('booking_success')
            else:
                messages.error(request, "Product not found.")
                return redirect('home')
                
        except Exception as e:
            print(f"Error creating booking: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('home')

    context = {
        'type': action_type,
        'product': product,
        'today_date': timezone.now().date(),
    }
    return render(request, 'rentalandbuy_booking.html', context)

def send_invoice_to_telegram(booking):
    """Generate PDF invoice and send it to Telegram as a document."""
    from app.models import GeneralInfo
    from django.template.loader import get_template
    import requests
    from django.conf import settings
    import os

    try:
        # 1. Render the invoice HTML
        template = get_template('invoice.html')
        html_string = template.render({
            'booking': booking,
            'general_info': GeneralInfo.objects.first()
        })

        # 2. Generate PDF and save to a temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            HTML(string=html_string, base_url=None).write_pdf(tmp_file)
            tmp_file_path = tmp_file.name

        # 3. Send the PDF to Telegram
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        
        with open(tmp_file_path, 'rb') as pdf_file:
            files = {
                'document': (
                    f'invoice_{booking.invoice_number}.pdf',
                    pdf_file,
                    'application/pdf'
                )
            }
            data = {
                'chat_id': chat_id,
                'caption': f"🧾 Invoice #{booking.invoice_number}\nCustomer: {booking.customer_name}"
            }
            response = requests.post(url, data=data, files=files)
            
            if response.status_code != 200:
                print(f"Error sending to Telegram: {response.text}")
                return False

        # 4. Clean up the temporary file
        os.unlink(tmp_file_path)
        return True

    except Exception as e:
        print(f"Error in send_invoice_to_telegram: {str(e)}")
        return False

def notify_client_approval(booking, approved=True):
    subject = "Your Request Has Been Approved" if approved else "Your Request Has Been Rejected"
    message = (
        f"Dear {booking.customer_name},\n\n"
        f"We are pleased to inform you that your request for "
        f"{booking.product.title if booking.product else 'our service'} has been "
        f"{'approved' if approved else 'rejected'}.\n\n"
        f"🧾 Booking Summary:\n"
        f"- Invoice Number: {booking.invoice_number}\n"
        f"- Order Type: {booking.order_type.capitalize()}\n"
        f"- Price: ${booking.price:,.2f}\n"
        f"- Status: {booking.status.capitalize()}\n"
        f"- Submitted On: {booking.submitted_at.strftime('%Y-%m-%d %H:%M')}\n"
    )
    if not approved and booking.rejection_reason:
        message += f"\n❗ Reason for rejection: {booking.rejection_reason}\n"
    message += (
        f"\nThank you for choosing SL Power. If you have any questions, feel free to contact vai Telegram https://t.me/Generator_cambodia .\n\n"
        f"Best regards,\n"
        f"The SL Power Team"
    )

    email = EmailMessage(
        subject,
        message,
        None,  # Uses DEFAULT_FROM_EMAIL
        [booking.email],
    )

    # Generate and attach PDF invoice if booking is approved
    if approved:
        try:
            template = get_template('invoice.html')
            html_string = template.render({'booking': booking, 'general_info': GeneralInfo.objects.first()})
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                HTML(string=html_string, base_url=None).write_pdf(tmp_file)
                tmp_file_path = tmp_file.name
            email.attach(f'invoice_{booking.invoice_number}.pdf', open(tmp_file_path, 'rb').read(), 'application/pdf')
            os.unlink(tmp_file_path)
        except Exception as e:
            print(f"Error generating or attaching invoice PDF: {e}")

    email.send(fail_silently=False)

@csrf_exempt
def telegram_webhook(request):
    # Debug prints removed for production cleanliness
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Debug prints removed
            callback_query = data.get('callback_query', {})
            if callback_query:
                callback_data = callback_query.get('data', '')
                message = callback_query.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                
                if len(callback_data.split('_')) == 2:
                    action, request_id = callback_data.split('_')
                elif len(callback_data.split('_')) == 3:
                    action, period, request_id = callback_data.split('_')
                    action = f"{action}_{period}"
                else:
                    return HttpResponse('Invalid callback data', status=400)
                
                # Try to get either a RentalBooking or ServiceRequest
                try:
                    booking = RentalBooking.objects.get(id=request_id)
                    request_type = 'booking'
                except RentalBooking.DoesNotExist:
                    try:
                        service_request = ServiceRequest.objects.get(id=request_id)
                        request_type = 'service'
                    except ServiceRequest.DoesNotExist:
                        return HttpResponse('Request not found', status=404)
                
                if request_type == 'booking':
                    # Handle rental/purchase booking callbacks
                    if action == 'approve':
                        if booking.order_type == 'rent':
                            months = (booking.return_date.year - booking.rental_date.year) * 12 + (booking.return_date.month - booking.rental_date.month)
                            if booking.return_date.day > booking.rental_date.day:
                                months += 1
                            if months <= 5:
                                # 1-5 months: show options
                                message = """
Rental Requests (1-5 months)

Please choose an approval option:
1. Approve for 1 month only
2. Approve full rental period
3. Reject the request
"""
                                keyboard = {
                                    "inline_keyboard": [
                                        [
                                            {"text": "Approve 1 Month", "callback_data": f"approve_1month_{booking.id}"},
                                            {"text": "Approve Full Period", "callback_data": f"approve_full_{booking.id}"}
                                        ],
                                        [
                                            {"text": "Reject", "callback_data": f"reject_{booking.id}"}
                                        ]
                                    ]
                                }
                                send_telegram_message(message, keyboard=keyboard)
                                return HttpResponse('OK')
                            else:
                                # 6+ months: direct approval with invoice
                                booking.status = 'approved'
                                booking.save()
                                approval_message = f"""
Order Approved!

Invoice: {booking.invoice_number}
Customer: {booking.customer_name}
Phone: {booking.phone}
Email: {booking.email}

Product: {booking.product.title if booking.product else 'N/A'}
Total: ${booking.price}
Deposit (30%): ${booking.deposit_amount}
Balance: ${booking.balance_amount}

Delivery: {booking.delivery_address}
Notes: {booking.notes or 'None'}

Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Payment Policy: For rentals of 6+ months, initial 1-month payment is required.
"""
                                send_telegram_message(approval_message)
                                send_invoice_to_telegram(booking)
                                notify_client_approval(booking, approved=True)
                                return HttpResponse('OK')
                        elif booking.order_type == 'buy':
                            message = f"""
Purchase Requests

A 10% booking deposit is required to confirm the purchase.

Please choose an action:
- Approve
- Reject request
"""
                            keyboard = {
                                "inline_keyboard": [
                                    [
                                        {"text": "Approve", "callback_data": f"approve_full_{booking.id}"}
                                    ],
                                    [
                                        {"text": "Reject", "callback_data": f"reject_{booking.id}"}
                                    ]
                                ]
                            }
                            send_telegram_message(message, keyboard=keyboard)
                            return HttpResponse('OK')
                    elif action == 'approve_1month':
                        from datetime import timedelta
                        booking.return_date = booking.rental_date + timedelta(days=30)
                        booking.status = 'approved'
                        booking.save()
                        approval_message = f"""
Order Approved (1 Month Only)!

Invoice: {booking.invoice_number}
Customer: {booking.customer_name}
Phone: {booking.phone}
Email: {booking.email}

Product: {booking.product.title if booking.product else 'N/A'}
Total: ${booking.price}
Deposit (30%): ${booking.deposit_amount}
Balance: ${booking.balance_amount}

Delivery: {booking.delivery_address}
Notes: {booking.notes or 'None'}

Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                        send_telegram_message(approval_message)
                        send_invoice_to_telegram(booking)
                    elif action == 'approve_full':
                        booking.status = 'approved'
                        booking.save()
                        approval_message = f"""
Order Approved (Full Period)!

Invoice: {booking.invoice_number}
Customer: {booking.customer_name}
Phone: {booking.phone}
Email: {booking.email}

Product: {booking.product.title if booking.product else 'N/A'}
Total: ${booking.price}
Deposit (30%): ${booking.deposit_amount}
Balance: ${booking.balance_amount}

Delivery: {booking.delivery_address}
Notes: {booking.notes or 'None'}

Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                        send_telegram_message(approval_message)
                        send_invoice_to_telegram(booking)
                    elif action == 'reject':
                        booking.status = 'rejected'
                        # Optionally, set rejection_reason here if you collect it from admin or bot
                        booking.save()
                        rejection_message = f"""
❌ Order Request Rejected

📋 Invoice: {booking.invoice_number}
👤 Customer: {booking.customer_name}
📞 Phone: {booking.phone}
📧 Email: {booking.email}

🔌 Product: {booking.product.title if booking.product else 'N/A'}
💰 Total: ${booking.price}

📅 Order Date: {booking.submitted_at.strftime('%Y-%m-%d %H:%M')}
🕒 Rejected: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                        if booking.rejection_reason:
                            rejection_message += f"\n❗ Reason for rejection: {booking.rejection_reason}\n"
                        rejection_message += "\nPlease contact the customer at {booking.phone} to discuss the rejection."
                        send_telegram_message(rejection_message)
                        notify_client_approval(booking, approved=False)
                    elif action == 'invoice':
                        send_invoice_to_telegram(booking)
                
                elif request_type == 'service':
                    # Handle service request callbacks
                    if action == 'approve':
                        service_request.status = 'in_progress'
                        service_request.save()
                        
                        # Calculate service costs
                        base_cost = 100  # Base service cost
                        onsite_fee = 50 if service_request.onsite_technician else 0
                        priority_fee = {
                            'low': 0,
                            'medium': 25,
                            'high': 50,
                            'urgent': 100
                        }.get(service_request.priority.lower(), 0)
                        
                        total_cost = base_cost + onsite_fee + priority_fee
                        
                        # Generate invoice number
                        invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{service_request.id:04d}"
                        
                        # Send approval message
                        message = f"""
✅ Service Request Approved

Service Request #{service_request.id} has been approved.

Customer: {service_request.customer_name}
Phone: {service_request.phone}
Email: {service_request.email if service_request.email else 'Not provided'}
Location: {service_request.location if service_request.location else 'Not provided'}

Service Details:
• Type: {service_request.service_type}
• Machine: {service_request.machine_type}
• Priority: {service_request.priority.title()}
• Onsite: {'Yes' if service_request.onsite_technician else 'No'}

Cost Breakdown:
• Base Service: ${base_cost}
• Onsite Fee: ${onsite_fee}
• Priority Fee: ${priority_fee}
• Total: ${total_cost}

Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                        # Send approval message
                        send_telegram_message(message)
                        
                        # Automatically generate and send invoice
                        try:
                            # Generate PDF invoice
                            template = get_template('service_invoice.html')
                            html_string = template.render({
                                'service_request': service_request,
                                'general_info': GeneralInfo.objects.first(),
                                'invoice_number': invoice_number,
                                'base_cost': base_cost,
                                'onsite_fee': onsite_fee,
                                'priority_fee': priority_fee,
                                'total_cost': total_cost
                            })

                            # Save PDF to temp file
                            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                                HTML(string=html_string, base_url=None).write_pdf(tmp_file)
                                tmp_file_path = tmp_file.name

                            # Send PDF to Telegram
                            bot_token = settings.TELEGRAM_BOT_TOKEN
                            chat_id = settings.TELEGRAM_CHAT_ID
                            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
                            
                            with open(tmp_file_path, 'rb') as pdf_file:
                                files = {
                                    'document': (
                                        f'service_invoice_{service_request.id}.pdf',
                                        pdf_file,
                                        'application/pdf'
                                    )
                                }
                                data = {
                                    'chat_id': chat_id,
                                    'caption': f"🧾 Service Invoice #{invoice_number}\nCustomer: {service_request.customer_name}"
                                }
                                response = requests.post(url, data=data, files=files)
                                
                                if response.status_code != 200:
                                    print(f"Error sending invoice to Telegram: {response.text}")
                                
                            # Clean up temp file
                            os.unlink(tmp_file_path)
                            
                        except Exception as e:
                            print(f"Error generating/sending invoice: {str(e)}")
                            # Send error message
                            error_message = f"⚠️ Error generating invoice: {str(e)}"
                            send_telegram_message(error_message)
                        
                    elif action == 'reject':
                        service_request.status = 'cancelled'
                        service_request.save()
                        send_telegram_message(f"Service Request #{service_request.id} has been rejected.")
                        
                    elif action == 'invoice_service':
                        # Generate and send service invoice
                        invoice_url = request.build_absolute_uri(
                            reverse('generate_service_invoice', args=[service_request.id])
                        )
                        message = f"🧾 Service Invoice #{service_request.id}\nClick here to view: {invoice_url}"
                        send_telegram_message(message)
                
                # Answer the callback query to remove the loading state
                bot_token = settings.TELEGRAM_BOT_TOKEN
                callback_id = callback_query.get('id')
                if callback_id:
                    answer_url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                    response = requests.post(answer_url, json={
                        "callback_query_id": callback_id,
                        "text": "Action completed"
                    })
                    print("Callback answer response:", response.json())
                
                return HttpResponse('OK')
            else:
                return HttpResponse('No callback query', status=400)
                
        except json.JSONDecodeError as e:
            return HttpResponse('Invalid JSON', status=400)
        except Exception as e:
            return HttpResponse(f'Error: {str(e)}', status=500)
    
    return HttpResponse('Method not allowed', status=405)

def service_request(request):
    if request.method == 'POST':
        # Get form data
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        location = request.POST.get('location', '')
        service_type = request.POST.get('service_type')
        machine_type = request.POST.get('machine_type')
        issue_description = request.POST.get('issue_description')
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time', '')
        priority = request.POST.get('priority', 'normal')
        onsite_technician = request.POST.get('onsite_technician') == 'on'
        notes = request.POST.get('notes', '')

        # Handle image upload
        image = request.FILES.get('image')
        
        # Create service request
        service_request = ServiceRequest.objects.create(
            customer_name=customer_name,
            phone=phone,
            email=email,
            location=location,
            service_type=service_type,
            machine_type=machine_type,
            issue_description=issue_description,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            priority=priority,
            onsite_technician=onsite_technician,
            notes=notes,
            image=image
        )

        # Send Telegram notification with image
        message = f"""
🔔 New Service Request

👤 Customer: {customer_name}
📞 Phone: {phone}
📧 Email: {email if email else 'Not provided'}
📍 Location: {location if location else 'Not provided'}

🔧 Service Details:
• Type: {service_type}
• Machine: {machine_type}
• Priority: {priority.title()}
• Onsite: {'Yes' if onsite_technician else 'No'}

📝 Issue Description:
{issue_description}

📅 Schedule:
• Date: {preferred_date}
• Time: {preferred_time if preferred_time else 'Not specified'}

📌 Notes: {notes if notes else 'None'}
"""
        
        # Create inline keyboard for Telegram with invoice link
        invoice_url = request.build_absolute_uri(
            reverse('generate_service_invoice', args=[service_request.id])
        )
        
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': '✅ Approve', 'callback_data': f'approve_{service_request.id}'},
                    {'text': '❌ Reject', 'callback_data': f'reject_{service_request.id}'}
                ],
                [
                    {'text': '🧾 Print Invoice', 'callback_data': f'invoice_service_{service_request.id}'}
                ]
            ]
        }

        # Send message with keyboard
        send_telegram_message(message, keyboard=keyboard)

        # If image was uploaded, send it separately
        if image:
            send_telegram_image(image)

        # Success message removed; handled by success page
        return redirect('booking_success')

    # Get service types and machine types for the form
    services = Service.objects.all()
    machine_types = [
        'Generator',
        'UPS',
        'ATS Panel',
        'Power Distribution Unit',
        'Battery System',
        'Solar Inverter',
        'Other'
    ]
    priorities = ServiceRequest.PRIORITY_CHOICES

    # Get initial service type from URL parameter
    initial_service_type = request.GET.get('service_type')

    context = {
        'services': services,
        'machine_types': machine_types,
        'priorities': priorities,
        'initial_service_type': initial_service_type
    }
    return render(request, 'service_request.html', context)

def send_telegram_image(image):
    """Send an image to Telegram"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    
    files = {
        'photo': image
    }
    
    data = {
        'chat_id': chat_id,
        'caption': '📸 Service Request Image'
    }
    
    response = requests.post(url, files=files, data=data)
    return response.json()

def generate_service_invoice(request, service_request_id):
    """Generate and display service invoice"""
    service_request = get_object_or_404(ServiceRequest, id=service_request_id)
    
    # Get company information
    company_info = CompanyInfo.objects.first()
    
    # Calculate costs
    base_cost = 100  # Base service cost
    onsite_fee = 50 if service_request.onsite_technician else 0
    priority_fee = {
        'low': 0,
        'normal': 0,
        'high': 25,
        'urgent': 50
    }.get(service_request.priority, 0)
    
    total_cost = base_cost + onsite_fee + priority_fee
    
    # Generate invoice number
    invoice_number = f"INV-{service_request.id:06d}"
    
    context = {
        'service_request': service_request,
        'company_info': company_info,
        'invoice_number': invoice_number,
        'base_cost': base_cost,
        'onsite_fee': onsite_fee,
        'priority_fee': priority_fee,
        'total_cost': total_cost
    }
    
    return render(request, 'service_invoice.html', context)

@csrf_exempt
def handle_telegram_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            callback_query = data.get('callback_query', {})
            callback_data = callback_query.get('data', '')
            chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
            
            if not chat_id:
                return JsonResponse({'status': 'error', 'message': 'No chat ID found'})
            
            if callback_data.startswith('approve_'):
                service_request_id = int(callback_data.split('_')[1])
                service_request = get_object_or_404(ServiceRequest, id=service_request_id)
                
                # Update service request status
                service_request.status = 'in_progress'
                service_request.save()
                
                # Generate invoice URL
                invoice_url = request.build_absolute_uri(
                    reverse('generate_service_invoice', args=[service_request_id])
                )
                
                # Send approval message with invoice link
                message = f"""
✅ Service Request Approved

Service Request #{service_request_id} has been approved.
Click below to view and print the invoice:
{invoice_url}
"""
                # Send message to the same chat
                send_telegram_message(message, chat_id=chat_id)
                
                return JsonResponse({'status': 'success'})
                
            elif callback_data.startswith('reject_'):
                service_request_id = int(callback_data.split('_')[1])
                service_request = get_object_or_404(ServiceRequest, id=service_request_id)
                
                # Update service request status
                service_request.status = 'cancelled'
                service_request.save()
                
                # Send rejection message
                message = f"""
❌ Service Request Rejected

Service Request #{service_request_id} has been rejected.
"""
                # Send message to the same chat
                send_telegram_message(message, chat_id=chat_id)
                
                return JsonResponse({'status': 'success'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def send_telegram_message(message, chat_id=None, keyboard=None):
    """Send message to Telegram"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        if not bot_token:
            return False

        # Use provided chat_id or default to the one in settings
        target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        data = {
            'chat_id': target_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        if keyboard:
            data['reply_markup'] = json.dumps(keyboard)
        
        response = requests.post(url, data=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {str(e)}")
        return False

def submit_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save()
            
            # Send to Google Sheets
            append_to_sheet(booking)
            
            # Send Telegram notification
            send_telegram_message("New booking submitted", booking)
            
            return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'booking_form.html', {'form': form})

def booking_success(request):
    return render(request, 'booking_success.html')