# posts/signals.py
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Comment, MessageNotification

@receiver(post_delete, sender=Comment)
def delete_notification_when_comment_deleted(sender, instance, **kwargs):
    MessageNotification.objects.filter(comment=instance).delete()



from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
