"""
URL configuration for Djangoweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app.views import (
    index,
    contact_form,
    product_detail,
    products,
    rental_booking,
    generate_invoice,
    telegram_webhook,
    service_request,
    generate_service_invoice,
    handle_telegram_callback,
    booking_success,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="home"),
    path('contact/', contact_form, name="contact_form"),
    path('product-detail/<product_id>', product_detail, name="product_detail"),
    path('products/', products, name="products"),
    path('rental-booking/', rental_booking, name='rental_booking'),
    path('invoice/<int:booking_id>/', generate_invoice, name='generate_invoice'),
    path('telegram/webhook/', telegram_webhook, name='telegram_webhook'),
    path('service-request/', service_request, name='service_request'),
    path('service/invoice/<int:service_request_id>/', generate_service_invoice, name='generate_service_invoice'),
    path('telegram/callback/', handle_telegram_callback, name='telegram_callback'),
    path('booking-success/', booking_success, name='booking_success'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)