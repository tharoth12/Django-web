from django.shortcuts import render , redirect
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator , PageNotAnInteger , EmptyPage
from app.models import ( 
   GeneralInfo ,
   Service ,
   Testimonial,
   FrequentlyAskedQuestion,
   ContactFormlog,
   Product,
   Author,
   HeroSection,
)
# Create your views here.
def index (request):

   general_info = GeneralInfo.objects.first()

   services = Service.objects.all()

   testimonials = Testimonial.objects.all()

   faqs= FrequentlyAskedQuestion.objects.all()

   hero_sections = HeroSection.objects.filter(is_active=True).order_by('display_order')

   recent_products = Product.objects.all()
   for product in recent_products:  
      print(f"product : {product}")
      print(f"product.created_at : {product.created_at}")
      print(f"product.author.product_name  : {product.author.product_name}")
      print(f"product.author.country  : {product.author.country}")
      print("")
   default_value = ""
   context = {
      "company_name":getattr(general_info, "company_name", default_value),
      "location":getattr(general_info, "location" , default_value),
      "email":getattr(general_info, "email", default_value),
      "phone":getattr(general_info , "phone",  default_value),
      "open_hours":getattr(general_info, "open_hours" , default_value),
      "video_url":getattr(general_info, "video_url" , default_value),
      "twitter_url":getattr (general_info, "Twitter_url", default_value),
      "facebook_url":getattr (general_info, "Facebook_url", default_value),
      "instagram_url":getattr(general_info, "instagram_url" ,default_value),
      "linkedin_url":getattr(general_info, "linkedin_url" ,default_value),
      "services":services,
      "testimonials" :testimonials,
      "faqs" : faqs,
      "recent_products": recent_products,
      "hero_sections" : hero_sections,
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
      product = Product.objects.get(id= product_id)

      recent_products = Product.objects.all().exclude(id=product_id).order_by("-created_at")[:2]
      
      context = {
         "product" : product,
         "recent_products": recent_products,
      }
      return render(request , "product_details.html" ,context)

def products(request):
      
      all_products = Product.objects.all().order_by("-created_at")
      product_per_page = 6
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