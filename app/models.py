from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

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
    user_image = models.ImageField( max_length= 255 , blank =True , null = True)
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

class Author(models.Model):
    product_name =models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    joined_at = models.DateField(null=True , blank= True)

    def __str__(self):
        return self.product_name
    

class Product(models.Model):
    product_image = models.FileField(max_length=255 , null=True , blank= True)
    category = models.CharField(max_length=50 , null=True , blank= True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author , on_delete=models.PROTECT , null= True , blank= True )
    created_at = models.DateField(default=timezone.now)
    content = RichTextField()  #models.TextField()

    def __str__(self):
        return self.title

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


        
