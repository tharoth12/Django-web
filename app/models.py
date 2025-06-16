from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from decimal import Decimal

# Create your models here.
class GeneralInfo(models.Model):
    company_name = models.CharField(max_length=255, default="Company Name")
    company_logo = models.ImageField( max_length=255 , blank = True , null = True)
    location = models.CharField( max_length=255)
    email = models.EmailField()
    phone = models.CharField( max_length=20)
    open_hours = models.CharField(max_length=100 , blank=True, null =True)
    video_url = models.URLField(blank=True , null=True)
    Telegram_url = models.URLField(blank=True , null=True)
    Facebook_url = models.URLField(blank=True , null=True)

    def __str__(self):
        return self.company_name
# Service 

class Service (models.Model):
    icon = models.CharField(max_length= 50 , blank = True , null= True)
    title = models.CharField(max_length=255 , unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title
    
class Testimonial(models.Model):
    user_image = models.ImageField(max_length=255, blank=True, null=True)
    star_count=[
        (1, 'One'),
        (2, 'Two'),
        (3, 'Three'),
        (4, 'Four'),
        (5, 'Five'),
    ]
    rating_count = models.IntegerField(choices=star_count)
    username = models.CharField(max_length=50)
    user_job_title = models.CharField(max_length=50)
    review = models.TextField()

    def __str__(self):
        return f"{self.username} - {self.user_job_title}"

class FrequentlyAskedQuestion(models.Model):
    question =models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question

class ContactFormlog(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    action_time = models.DateTimeField (null= True , blank= True)
    is_success = models.BooleanField(default=False)
    is_error =models.BooleanField(default=False)
    error_message = models.TextField(null= True , blank= True)
    
    def __str__(self):
        return self.email

class Product(models.Model):
    FUEL_TYPE_CHOICES = [
        ('diesel', 'Diesel'),
        ('petrol', 'Petrol'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('for_rent', 'For Rent'),
        ('out_of_stock', 'Out of Stock'),
    ]

    title = models.CharField(max_length=255)  # Machine name
    product_image = models.ImageField(upload_to='products/' , null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rent_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Basic Product Specs
    power_output = models.CharField(max_length=50, null=True, blank=True)
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPE_CHOICES, default='diesel')
    phase = models.CharField(max_length=50, null=True, blank=True)
    noise_level = models.CharField(max_length=50, null=True, blank=True)
    tank_capacity = models.CharField(max_length=50, null=True, blank=True)
    runtime = models.CharField(max_length=100, null=True, blank=True)
    
    # Service & Support Info
    free_delivery = models.BooleanField(default=False)
    warranty_period = models.CharField(max_length=50, null=True, blank=True)
    installation_time = models.CharField(max_length=100, null=True, blank=True)
    technical_support = models.BooleanField(default=True)
    replacement_guarantee = models.CharField(max_length=100, null=True, blank=True)
    
    # Rental Options
    rental_duration = models.CharField(max_length=100, null=True, blank=True)
    maintenance_plan = models.BooleanField(default=False)
    
    # Optional Add-ons
    ats_panel = models.BooleanField(default=False)
    onsite_technician = models.BooleanField(default=False)
    power_backup_design = models.BooleanField(default=False)
    
    # Legacy fields (keeping for backward compatibility)
    kva = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    kwg = models.CharField(max_length=100, null=True, blank=True)
    specification = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_additional_images(self):
        """Returns a list of additional images for the product"""
        return self.images.all()[:2]  # Get up to 2 additional images

    def get_status_badge_class(self):
        """Returns the appropriate Bootstrap badge class based on status"""
        status_classes = {
            'available': 'bg-success',
            'for_rent': 'bg-primary',
            'out_of_stock': 'bg-danger'
        }
        return status_classes.get(self.status, 'bg-secondary')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/additional/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Image for {self.product.title}"

class HeroSection(models.Model):
    tag_lines = models.CharField(max_length=255)
    hero_img = models.ImageField(max_length = 255 , null = True , blank = True)
    video_url = models.URLField(blank= True , null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Sections"
        ordering = ['display_order']

    def __str__(self):
        return self.tag_lines

class RentalBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('deposit_paid', 'Deposit Paid'),
        ('fully_paid', 'Fully Paid'),
    ]

    # Basic Info
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    location = models.CharField(max_length=255)
    
    # Order Details
    order_type = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('rent', 'Rent')], default='rent')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, related_name='rental_bookings')
    rental_date = models.DateField(help_text="Start date of the rental", default=timezone.now)
    return_date = models.DateField(help_text="End date of the rental", null=True, blank=True)
    
    # Financial Info
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Additional Info
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='order_images/', blank=True, null=True)
    
    # Optional Services
    ats_panel = models.BooleanField(default=False)
    onsite_technician = models.BooleanField(default=False)
    power_backup_design = models.BooleanField(default=False)
    
    # Status & Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.customer_name} - {self.order_type} - {self.product.title if self.product else 'No Product'}"

    def save(self, *args, **kwargs):
        # Generate invoice number if not exists
        if not self.invoice_number and self.status == 'approved':
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{self.id:04d}"
        
        # Calculate deposit and balance if price exists
        if self.price:
            # Convert price to Decimal if it's a float
            price_decimal = Decimal(str(self.price)) if isinstance(self.price, float) else self.price
            self.deposit_amount = price_decimal * Decimal('0.30')  # 30% deposit
            self.balance_amount = price_decimal - self.deposit_amount
        
        super().save(*args, **kwargs)

    def get_total_optional_services(self):
        total = 0
        if self.ats_panel:
            total += 300
        if self.onsite_technician:
            total += 100
        if self.power_backup_design:
            total += 50
        return total

class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Customer Information
    customer_name = models.CharField(max_length=100, default='Anonymous')
    email = models.EmailField(blank=True, null=True)  # Optional
    phone = models.CharField(max_length=20, default='N/A')
    location = models.CharField(max_length=255, blank=True, null=True)  # Optional
    
    # Service Details
    service_type = models.CharField(max_length=100, default='Maintenance', help_text="Type of service (e.g., Maintenance, Repair, Installation)")
    machine_type = models.CharField(max_length=100, default='Generator', help_text="Type of machine (e.g., Generator, UPS)")
    issue_description = models.TextField(default='No description provided')
    preferred_date = models.DateField(default=timezone.now)
    preferred_time = models.TimeField(null=True, blank=True)
    
    # Additional Information
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    image = models.ImageField(upload_to='service_issues/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Cost Information
    onsite_technician = models.BooleanField(default=False)
    onsite_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    final_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_technician = models.CharField(max_length=100, blank=True, null=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    actual_completion = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} - {self.service_type} ({self.status})"

    def get_total_cost(self):
        total = Decimal('0.00')
        if self.onsite_technician:
            total += self.onsite_fee
        if self.final_cost:
            total += self.final_cost
        return total

    class Meta:
        ordering = ['-submitted_at']

class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('rental', 'Rental'),
        ('technical', 'Technical'),
        ('payment', 'Payment'),
        ('service', 'Service'),
    ]

    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'created_at']

    def __str__(self):
        return self.question

class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('rental', 'Rental Inquiry'),
        ('technical', 'Technical Support'),
        ('service', 'Service Request'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

