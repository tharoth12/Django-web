from django.contrib import admin
from app.models import (
     GeneralInfo,
     Service ,
     Testimonial ,
     FrequentlyAskedQuestion,
     ContactFormlog ,
     Product,
     Author,
     HeroSection,
)

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

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  
    list_display = [
       'category',
       'title',
       'product_image',
       'created_at',
    ]
    
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display =[
        'product_name',
    ]
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