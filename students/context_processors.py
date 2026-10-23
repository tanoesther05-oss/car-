from .models import StudyLevel

def navigation(request):
    return {"nav_levels": StudyLevel.objects.all()}
