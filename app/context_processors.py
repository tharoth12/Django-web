from .models import GeneralInfo, HeroSection

def general_info(request):
    try:
        info = GeneralInfo.objects.first()  # Or filter by something if needed
    except GeneralInfo.DoesNotExist:
        info = None
    hero_sections = HeroSection.objects.filter(is_active=True).order_by('display_order')
    return {
        'general_info': info,
        'hero_sections': hero_sections
    }
