from posts.models import ReportMessage

def report_bell_alert(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return {
            'report_bell_alert': ReportMessage.objects.filter(
                is_admin_replied=False
            ).exists()
        }
    return {'report_bell_alert': False}
