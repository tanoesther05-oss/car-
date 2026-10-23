from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
from .models import Student

@receiver(post_save, sender=Student)
def log_student_save(sender, instance, created, **kwargs):
    # L'historique détaillé des changements est aussi conservé par l'administration Django.
    pass
