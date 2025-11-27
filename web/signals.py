from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import ReportMessage

@receiver(post_save, sender=ReportMessage)
def notify_user_on_admin_reply(sender, instance, created, **kwargs):
    if not created and instance.is_admin_replied and instance.admin_reply:
        send_mail(
            subject='Admin replied to your report',
            message=f"Admin says:\n\n{instance.admin_reply}",
            from_email='admin@example.com',
            recipient_list=[instance.user.email],
            fail_silently=False,
        )
