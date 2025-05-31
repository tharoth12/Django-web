from .models import GeneralInfo

def general_info(request):
    try:
        info = GeneralInfo.objects.first()  # Or filter by something if needed
    except GeneralInfo.DoesNotExist:
        info = None
    return {
        'general_info': info
    }
