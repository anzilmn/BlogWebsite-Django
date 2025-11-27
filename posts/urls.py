from django.urls import path, include
from posts import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "posts"

urlpatterns = [
    path('create/', views.create_post, name="create_post"),
    path('my-posts/', views.my_posts, name="my_posts"),
    path('delete/<int:id>/', views.delete_post, name="delete_post"),
    path('draft/<int:id>/', views.draft_post, name="draft_post"),
    path('edit/<int:id>/', views.edit_post, name="edit_post"),
    path('admin/user/<int:user_id>/posts/', views.admin_user_posts, name='admin_user_posts'),
    path('profile/', views.profile_view, name='profile'),
    path('manage-suspensions/', views.manage_suspensions, name='manage_suspensions'),
    path('suspend/<int:pk>/', views.suspend_user, name='suspend_user'),
    path('unsuspend/<int:pk>/', views.unsuspend_user, name='unsuspend_user'),




    

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)