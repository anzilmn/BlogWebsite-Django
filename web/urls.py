from django.urls import path
from .views import index,post  # Import the index function
from .views import delete_comment ,add_ajax_comment,delete_ajax_comment,report_comment,my_reports,notifications_view,delete_all_notifications,delete_all_reports,report_messages_admin_view,edit_report_message

app_name = "web"  # This must match the namespace used in include()

urlpatterns = [
    path("", index, name="index"),
    path("<int:id>/", post, name="post"),
    path("comment/delete/<int:id>/", delete_comment, name="delete_comment"),
    path('add_comment/', add_ajax_comment, name='add_ajax_comment'),
    path('delete_comment/<int:comment_id>/', delete_ajax_comment, name='delete_ajax_comment'),
    path('report_comment/<int:comment_id>/', report_comment, name='report_comment'),
    path('my_reports/',   my_reports, name='my_reports'),
     path("messages/",  notifications_view, name="messages"),
 
    path('messages/delete-all/', delete_all_notifications, name='delete_all_notifications'),
    path('my-reports/delete-all/',delete_all_reports, name='delete_all_reports'),
    path('reported-messages/', report_messages_admin_view, name='admin_reports'),
    path('report/<int:report_id>/edit/', edit_report_message, name='edit_report_message'),



]
