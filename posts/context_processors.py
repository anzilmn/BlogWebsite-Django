# posts/context_processors.py
from posts.models import MessageNotification

def bell_alert(request):
    if request.user.is_authenticated:
        has_unseen = MessageNotification.objects.filter(post_owner=request.user, seen=False).exists()
        return {'bell_alert': has_unseen}
    return {'bell_alert': False}
