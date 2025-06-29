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
   ContactMessage,
)
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
from django.templatetags.static import static
from django.utils.html import strip_tags
from django.urls import reverse
from django.http import JsonResponse
from .utils import append_to_sheet, update_sheet_status
from django.db.models import Q

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
        print("\nUser has submitted a contact form\n")
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Create contact message
        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            created_at=timezone.now()
        )

        # Prepare email context
        context = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "time": timezone.now()
        }
        try:
            html_content = render_to_string('email.html', context)
            print("Email template rendered successfully")
        except Exception as e:
            print(f"Error rendering email template: {str(e)}")
            messages.error(request, "There was an error processing your message. Please try again.")
            return redirect('home')

        # Send email
        try:
            # First try to send email
            send_mail(
                subject=subject,
                message=None,
                html_message=html_content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            
            # If email sent successfully, send Telegram notification
            telegram_message = f"""
📨 New Contact Message

👤 From: {name}
📧 Email: {email}
📝 Subject: {subject}

💬 Message:
{message}

⏰ Time: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
            send_telegram_message(telegram_message)
            
            # Store success message in session
            request.session['success_message'] = "Your message has been sent successfully! We will contact you soon."
            return redirect('booking_success')
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            error_message = str(e)
            
            # Log the error with more details
            ContactFormlog.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                action_time=timezone.now(),
                is_success=False,
                is_error=True,
                error_message=error_message
            )
            
            # Check if it's an authentication error
            if "Authentication Required" in error_message:
                messages.error(request, "Email service configuration error. Please contact the administrator.")
            elif "SMTP" in error_message:
                messages.error(request, "Email service temporarily unavailable. Please try again later.")
            else:
                messages.error(request, "There was an error sending your message. Please try again later.")
            
            # Still send Telegram notification even if email fails
            telegram_message = f"""
⚠️ New Contact Message (Email Failed)

👤 From: {name}
📧 Email: {email}
📝 Subject: {subject}

💬 Message:
{message}

⏰ Time: {timezone.now().strftime('%Y-%m-%d %H:%M')}

❌ Email Error: {error_message}
"""
            send_telegram_message(telegram_message)
            return redirect('home')

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
    # Get search query from GET parameters
    search_query = request.GET.get('search', '')
    
    # Base queryset
    all_products = Product.objects.all()
    similar_products = None
    no_matches = False
    
    # Apply search filter if query exists
    if search_query:
        # First try exact matches
        exact_matches = all_products.filter(
            Q(title__icontains=search_query) |
            Q(power_output__icontains=search_query) |
            Q(fuel_type__icontains=search_query) |
            Q(phase__icontains=search_query) |
            Q(kva__icontains=search_query) |
            Q(country__icontains=search_query)
        )
        
        if exact_matches.exists():
            all_products = exact_matches
        else:
            # If no exact matches, find similar products
            # Split search query into words
            search_words = search_query.split()
            
            # Create a Q object for each word
            similar_queries = Q()
            for word in search_words:
                if len(word) > 2:  # Only consider words longer than 2 characters
                    similar_queries |= (
                        Q(title__icontains=word) |
                        Q(power_output__icontains=word) |
                        Q(fuel_type__icontains=word) |
                        Q(phase__icontains=word) |
                        Q(kva__icontains=word) |
                        Q(country__icontains=word)
                    )
            
            # Get similar products
            similar_products = all_products.filter(similar_queries).distinct()
            
            if similar_products.exists():
                all_products = similar_products
            else:
                # If no similar products found, show all products
                no_matches = True
                all_products = Product.objects.all().order_by("-created_at")
    
    # Order by creation date
    all_products = all_products.order_by("-created_at")
    
    # Pagination
    product_per_page = 9
    paginator = Paginator(all_products, product_per_page)
    
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        "products": products,
        "search_query": search_query,
        "is_similar_results": similar_products is not None and not exact_matches.exists() if search_query else False,
        "no_matches": no_matches,
    }
    return render(request, "products.html", context)

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
                            {"text": "✅ Approve", "callback_data": f"approve_{booking.id}"},
                            {"text": "❌ Reject", "callback_data": f"reject_{booking.id}"}
                        ],
                        [
                            {"text": "🧾 Print Invoice", "callback_data": f"invoice_{booking.id}"}
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
        
        print("\nSending Telegram message with data:", json.dumps(data, indent=2))
        response = requests.post(url, json=data)
        print("Telegram API response:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error sending telegram message: {str(e)}")
        return None

def generate_invoice(request, booking_id):
    booking = get_object_or_404(RentalBooking, id=booking_id)
    general_info = GeneralInfo.objects.first()
    
    # Get the absolute URL for the QR code image
    # For production (PythonAnywhere), use the full domain
    if settings.ENVIRONMENT == 'production':
        qr_code_url = f"https://tharoth.pythonanywhere.com{static('assets/img/QR.jpg')}"
    else:
        # For development, use the request to build absolute URL
        qr_code_url = request.build_absolute_uri(static('assets/img/QR.jpg'))
    
    # Alternative: Use data URI for QR code to avoid static file issues
    try:
        qr_image_path = os.path.join(settings.STATIC_ROOT, 'assets', 'img', 'QR.jpg')
        if not os.path.exists(qr_image_path):
            qr_image_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'QR.jpg')
        
        if os.path.exists(qr_image_path):
            import base64
            with open(qr_image_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                qr_code_url = f"data:image/jpeg;base64,{img_data}"
                print("Using data URI for QR code")
        else:
            print(f"QR image not found at: {qr_image_path}")
    except Exception as e:
        print(f"Error creating data URI for QR code: {e}")
        # Fall back to URL approach
    
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"QR Code URL: {qr_code_url}")  # Debug log
    print(f"Static URL: {static('assets/img/QR.jpg')}")  # Debug log
    
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
    
    # Debug log for context
    print(f"Context data: {context}")
    
    html_string = render_to_string('invoice.html', context)
    
    # Create PDF with absolute URLs
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        # Use the same base URL logic for WeasyPrint
        if settings.ENVIRONMENT == 'production':
            base_url = 'https://tharoth.pythonanywhere.com/'
        else:
            base_url = request.build_absolute_uri('/')
            
        HTML(
            string=html_string,
            base_url=base_url
        ).write_pdf(tmp_file)
        tmp_file_path = tmp_file.name
    
    response = HttpResponse(open(tmp_file_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'filename="invoice_{booking.invoice_number}.pdf"'
    
    # Clean up the temporary file
    os.unlink(tmp_file_path)
    
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
        # Fallback if rental_date is missing or empty
        if not rental_date:
            rental_date = timezone.now().date()
            
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
                return render(request, 'booking_success.html')
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
    import os

    try:
        # 1. Render the invoice HTML with proper QR code URL
        template = get_template('invoice.html')
        
        # Get the absolute URL for the QR code image
        # For production (PythonAnywhere), use the full domain
        if settings.ENVIRONMENT == 'production':
            qr_code_url = f"https://tharoth.pythonanywhere.com{static('assets/img/QR.jpg')}"
        else:
            # For development, construct a basic URL
            qr_code_url = f"http://localhost:8000{static('assets/img/QR.jpg')}"
        
        # Alternative: Use data URI for QR code to avoid static file issues
        try:
            qr_image_path = os.path.join(settings.STATIC_ROOT, 'assets', 'img', 'QR.jpg')
            if not os.path.exists(qr_image_path):
                qr_image_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'QR.jpg')
            
            if os.path.exists(qr_image_path):
                import base64
                with open(qr_image_path, 'rb') as img_file:
                    img_data = base64.b64encode(img_file.read()).decode('utf-8')
                    qr_code_url = f"data:image/jpeg;base64,{img_data}"
                    print("Using data URI for QR code in send_invoice_to_telegram")
            else:
                print(f"QR image not found at: {qr_image_path}")
        except Exception as e:
            print(f"Error creating data URI for QR code in send_invoice_to_telegram: {e}")
            # Fall back to URL approach
        
        # Calculate rental months if it's a rental order
        months = None
        if booking.order_type == 'rent' and booking.rental_date and booking.return_date:
            months = (booking.return_date.year - booking.rental_date.year) * 12 + (booking.return_date.month - booking.rental_date.month)
            if booking.return_date.day > booking.rental_date.day:
                months += 1
            months = max(1, months)  # Ensure at least 1 month
        
        html_string = template.render({
            'booking': booking,
            'general_info': GeneralInfo.objects.first(),
            'qr_code_url': qr_code_url,
            'months': months,
        })

        # 2. Generate PDF and save to a temp file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            # Use the same base URL logic for WeasyPrint
            if settings.ENVIRONMENT == 'production':
                base_url = 'https://tharoth.pythonanywhere.com/'
            else:
                base_url = 'http://localhost:8000/'
                
            HTML(string=html_string, base_url=base_url).write_pdf(tmp_file)
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
    try:
        subject = "Your Request Has Been Approved" if approved else "Your Request Has Been Rejected"
        
        # Create context for email template
        context = {
            'booking': booking,
            'approved': approved,
            'company_info': GeneralInfo.objects.first()
        }
        
        # Render HTML email template
        html_message = render_to_string('email.html', context)
        
        # Create EmailMessage object
        email = EmailMessage(
            subject=subject,
            body=html_message,  # Use HTML message directly
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        
        # Set content type to HTML
        email.content_subtype = 'html'
        
        # Generate and attach PDF invoice if booking is approved
        if approved:
            try:
                # Generate invoice PDF with proper QR code URL
                template = get_template('invoice.html')
                
                # Get the absolute URL for the QR code image
                # For production (PythonAnywhere), use the full domain
                if settings.ENVIRONMENT == 'production':
                    qr_code_url = f"https://tharoth.pythonanywhere.com{static('assets/img/QR.jpg')}"
                else:
                    # For development, construct a basic URL
                    qr_code_url = f"http://localhost:8000{static('assets/img/QR.jpg')}"
                
                # Alternative: Use data URI for QR code to avoid static file issues
                try:
                    qr_image_path = os.path.join(settings.STATIC_ROOT, 'assets', 'img', 'QR.jpg')
                    if not os.path.exists(qr_image_path):
                        qr_image_path = os.path.join(settings.BASE_DIR, 'static', 'assets', 'img', 'QR.jpg')
                    
                    if os.path.exists(qr_image_path):
                        import base64
                        with open(qr_image_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            qr_code_url = f"data:image/jpeg;base64,{img_data}"
                            print("Using data URI for QR code in notify_client_approval")
                    else:
                        print(f"QR image not found at: {qr_image_path}")
                except Exception as e:
                    print(f"Error creating data URI for QR code in notify_client_approval: {e}")
                    # Fall back to URL approach
                
                # Calculate rental months if it's a rental order
                months = None
                if booking.order_type == 'rent' and booking.rental_date and booking.return_date:
                    months = (booking.return_date.year - booking.rental_date.year) * 12 + (booking.return_date.month - booking.rental_date.month)
                    if booking.return_date.day > booking.rental_date.day:
                        months += 1
                    months = max(1, months)  # Ensure at least 1 month
                
                html_string = template.render({
                    'booking': booking,
                    'general_info': GeneralInfo.objects.first(),
                    'qr_code_url': qr_code_url,
                    'months': months,
                })
                
                # Create PDF in memory
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    # Use the same base URL logic for WeasyPrint
                    if settings.ENVIRONMENT == 'production':
                        base_url = 'https://tharoth.pythonanywhere.com/'
                    else:
                        base_url = 'http://localhost:8000/'
                        
                    HTML(string=html_string, base_url=base_url).write_pdf(tmp_file)
                    tmp_file_path = tmp_file.name
                
                # Attach PDF to email
                with open(tmp_file_path, 'rb') as pdf_file:
                    email.attach(f'invoice_{booking.invoice_number}.pdf', pdf_file.read(), 'application/pdf')
                
                # Clean up temp file
                os.unlink(tmp_file_path)
                
            except Exception as e:
                print(f"[notify_client_approval] Error generating invoice PDF: {e}")
                # Continue sending email even if PDF generation fails
                send_telegram_message(f"⚠️ Error generating invoice PDF for booking #{booking.id}: {str(e)}")
        
        # Send email
        email.send(fail_silently=False)
        
        print(f"[notify_client_approval] Email sent successfully to {booking.email}")
        
        # Log successful email
        ContactFormlog.objects.create(
            email=booking.email,
            subject=subject,
            message=html_message,
            action_time=timezone.now(),
            is_success=True,
            is_error=False
        )
        
        return True
        
    except Exception as e:
        error_message = f"Error sending email: {str(e)}"
        print(f"[notify_client_approval] {error_message}")
        
        # Log failed email attempt
        ContactFormlog.objects.create(
            email=booking.email,
            subject=subject if 'subject' in locals() else 'Email Failed',
            message=error_message,
            action_time=timezone.now(),
            is_success=False,
            is_error=True,
            error_message=error_message
        )
        
        # Send error notification via Telegram
        telegram_message = f"""
⚠️ Email Delivery Failed

Failed to send email to: {booking.email}
Order: {booking.invoice_number}
Error: {error_message}

Please check the email settings and retry manually if needed.
"""
        send_telegram_message(telegram_message)
        
        return False

@csrf_exempt
def telegram_webhook(request):
    if request.method == 'GET':
        return HttpResponse('Webhook is working!')
        
    elif request.method == 'POST':
        try:
            # Parse JSON data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                return HttpResponse('Invalid JSON', status=400)
            
            # Handle callback queries
            callback_query = data.get('callback_query', {})
            if callback_query:
                callback_data = callback_query.get('data', '')
                message = callback_query.get('message', {})
                chat_id = message.get('chat', {}).get('id')
                
                parts = callback_data.split('_')
                
                # Handle both 2-part (rental) and 3-part (service) callback data
                if len(parts) == 2:  # Rental booking callbacks
                    action, request_id = parts
                    try:
                        booking = RentalBooking.objects.get(id=request_id)
                        
                        if action == 'approve':
                            booking.status = 'approved'
                            booking.save()
                            update_sheet_status(booking)
                            
                            # Send single approval notification
                            approval_message = f"""
✅ Rental Request #{booking.id} Approved

📋 Invoice: {booking.invoice_number}
👤 Customer: {booking.customer_name}
📞 Phone: {booking.phone}
📧 Email: {booking.email}

🔌 Product: {booking.product.title if booking.product else 'N/A'}
💰 Total: ${booking.price:,.2f}
💵 Deposit (30%): ${booking.deposit_amount:,.2f}
💳 Balance: ${booking.balance_amount:,.2f}

📍 Delivery: {booking.delivery_address or 'Not specified'}
📝 Notes: {booking.notes or 'None'}

⏰ Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                            send_telegram_message(approval_message)
                            send_invoice_to_telegram(booking)
                            
                            # Send email silently
                            try:
                                notify_client_approval(booking, approved=True)
                            except Exception as e:
                                print(f"Error sending approval email: {str(e)}")
                            
                        elif action == 'reject':
                            booking.status = 'rejected'
                            booking.save()
                            update_sheet_status(booking)
                            
                            # Send single rejection notification
                            rejection_message = f"""
❌ Rental Request #{booking.id} Rejected

📋 Invoice: {booking.invoice_number}
👤 Customer: {booking.customer_name}
📞 Phone: {booking.phone}
📧 Email: {booking.email}

🔌 Product: {booking.product.title if booking.product else 'N/A'}
💰 Total: ${booking.price:,.2f}

📅 Order Date: {booking.submitted_at.strftime('%Y-%m-%d %H:%M')}
⏰ Rejected: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please contact the customer to discuss the rejection.
"""
                            send_telegram_message(rejection_message)
                            
                            # Send email silently
                            try:
                                notify_client_approval(booking, approved=False)
                            except Exception as e:
                                print(f"Error sending rejection email: {str(e)}")
                                
                        elif action == 'invoice':
                            send_invoice_to_telegram(booking)
                        else:
                            return HttpResponse('Invalid action', status=400)
                            
                    except RentalBooking.DoesNotExist:
                        error_message = f"⚠️ Could not find rental booking #{request_id}. The booking may have been deleted."
                        send_telegram_message(error_message)
                        
                        # Show error in Telegram UI
                        bot_token = settings.TELEGRAM_BOT_TOKEN
                        callback_id = callback_query.get('id')
                        if callback_id:
                            answer_url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                            requests.post(answer_url, json={
                                "callback_query_id": callback_id,
                                "text": "Error: Booking not found",
                                "show_alert": True
                            })
                        return HttpResponse('OK')
                        
                elif len(parts) == 3:  # Service request callbacks
                    action_type, action, request_id = parts
                    
                    if action_type == 'service':
                        try:
                            service_request = ServiceRequest.objects.get(id=request_id)
                        except ServiceRequest.DoesNotExist:
                            error_message = f"⚠️ Could not find service request #{request_id}. The request may have been deleted."
                            send_telegram_message(error_message)
                            
                            # Show error in Telegram UI
                            bot_token = settings.TELEGRAM_BOT_TOKEN
                            callback_id = callback_query.get('id')
                            if callback_id:
                                answer_url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                                requests.post(answer_url, json={
                                    "callback_query_id": callback_id,
                                    "text": "Error: Service request not found",
                                    "show_alert": True
                                })
                            return HttpResponse('OK')

                        if action == 'approve':
                            service_request.status = 'in_progress'
                            service_request.save()
                            
                            # Send single approval notification
                            approval_message = f"""
✅ Service Request #{service_request.id} Approved

👤 Customer: {service_request.customer_name}
📞 Phone: {service_request.phone}
📧 Email: {service_request.email}

🔧 Service Details:
• Type: {service_request.service_type}
• Machine: {service_request.machine_type}
• Priority: {service_request.priority}
• Onsite: {'Yes' if service_request.onsite_technician else 'No'}

📅 Schedule:
• Date: {service_request.preferred_date}
• Time: {service_request.preferred_time or 'Not specified'}

⏰ Approved: {timezone.now().strftime('%Y-%m-%d %H:%M')}
"""
                            send_telegram_message(approval_message)
                            
                            # Send email silently
                            if service_request.email:
                                try:
                                    subject = "Your Service Request Has Been Approved"
                                    message = (
                                        f"Dear {service_request.customer_name},\n\n"
                                        f"Your service request for {service_request.machine_type} ({service_request.service_type}) has been approved.\n"
                                        f"Our team will contact you soon to schedule the service.\n\n"
                                        f"Service Details:\n"
                                        f"- Type: {service_request.service_type}\n"
                                        f"- Machine: {service_request.machine_type}\n"
                                        f"- Priority: {service_request.priority}\n"
                                        f"- Scheduled Date: {service_request.preferred_date}\n"
                                        f"- Scheduled Time: {service_request.preferred_time or 'Not specified'}\n\n"
                                        f"If you need to reschedule or have any questions, please contact us.\n\n"
                                        f"Best regards,\nSL Power Team"
                                    )
                                    send_mail(
                                        subject,
                                        message,
                                        settings.DEFAULT_FROM_EMAIL,
                                        [service_request.email],
                                        fail_silently=True
                                    )
                                except Exception as e:
                                    print(f"Error sending approval email: {str(e)}")

                        elif action == 'reject':
                            service_request.status = 'cancelled'
                            service_request.save()
                            
                            # Send single rejection notification
                            rejection_message = f"""
❌ Service Request #{service_request.id} Rejected

👤 Customer: {service_request.customer_name}
📞 Phone: {service_request.phone}
📧 Email: {service_request.email}

🔧 Service Details:
• Type: {service_request.service_type}
• Machine: {service_request.machine_type}
• Priority: {service_request.priority}

⏰ Rejected: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Please contact the customer to discuss alternative solutions.
"""
                            send_telegram_message(rejection_message)
                            
                            # Send email silently
                            if service_request.email:
                                try:
                                    subject = "Your Service Request Status Update"
                                    message = (
                                        f"Dear {service_request.customer_name},\n\n"
                                        f"Regarding your service request for {service_request.machine_type}:\n\n"
                                        f"We regret to inform you that we are unable to process your request at this time. "
                                        f"Our team will contact you shortly to discuss alternative solutions.\n\n"
                                        f"Service Details:\n"
                                        f"- Type: {service_request.service_type}\n"
                                        f"- Machine: {service_request.machine_type}\n"
                                        f"- Requested Date: {service_request.preferred_date}\n\n"
                                        f"If you have any questions, please don't hesitate to contact us.\n\n"
                                        f"Best regards,\nSL Power Team"
                                    )
                                    send_mail(
                                        subject,
                                        message,
                                        settings.DEFAULT_FROM_EMAIL,
                                        [service_request.email],
                                        fail_silently=True
                                    )
                                except Exception as e:
                                    print(f"Error sending rejection email: {str(e)}")
                        else:
                            return HttpResponse('Invalid action', status=400)
                    else:
                        return HttpResponse('Invalid action type', status=400)
                
                # Answer the callback query
                bot_token = settings.TELEGRAM_BOT_TOKEN
                callback_id = callback_query.get('id')
                if callback_id:
                    answer_url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
                    requests.post(answer_url, json={
                        "callback_query_id": callback_id,
                        "text": "Action completed successfully"
                    })
                
                return HttpResponse('OK')
            else:
                return HttpResponse('No callback query', status=400)
                
        except Exception as e:
            error_message = f"⚠️ Webhook error: {str(e)}"
            send_telegram_message(error_message)
            return HttpResponse('Internal error', status=500)
    
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
        
        # Create inline keyboard for Telegram
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': '✅ Approve', 'callback_data': f'service_approve_{service_request.id}'},
                    {'text': '❌ Reject', 'callback_data': f'service_reject_{service_request.id}'}
                ]
            ]
        }

        # Send message with keyboard
        send_telegram_message(message, keyboard=keyboard)
        # If image was uploaded, send it separately
        if image:
            send_telegram_image(image)

        # Send confirmation email
        if email:
            subject = "Thank you for your service request"
            message = (
                f"Dear {customer_name},\n\n"
                "Thank you for requesting our service. "
                "Our team has received your request and will contact you soon to follow up.\n\n"
                "Best regards,\nSL Power Team"
            )
            send_mail(
                subject,
                message,
                None,  # Uses DEFAULT_FROM_EMAIL
                [email],
                fail_silently=True,
            )

        return render(request, 'booking_success.html')

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
    # Get success message from session
    success_message = request.session.get('success_message')
    # Clear the session message
    if 'success_message' in request.session:
        del request.session['success_message']
    
    context = {
        'success_message': success_message
    }
    return render(request, 'booking_success.html', context)

def test_qr_code(request):
    """Test view to debug QR code URL generation"""
    from django.http import JsonResponse
    
    # Test different URL generation methods
    static_url = static('assets/img/QR.jpg')
    
    if settings.ENVIRONMENT == 'production':
        qr_code_url = f"https://tharoth.pythonanywhere.com{static_url}"
    else:
        qr_code_url = request.build_absolute_uri(static_url)
    
    return JsonResponse({
        'environment': settings.ENVIRONMENT,
        'static_url': static_url,
        'qr_code_url': qr_code_url,
        'debug': settings.DEBUG,
        'static_root': settings.STATIC_ROOT,
        'static_url_setting': settings.STATIC_URL,
    })