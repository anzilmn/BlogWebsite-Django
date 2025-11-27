 
from django.urls import path,include
from users import views


app_name = "users"
urlpatterns = [
   
   
   path("logout/", views.user_logout, name="logout"),
   path('sign_log/',views.sign_log , name="sign_log" ),
   path('users_list/',views.users_list , name="users_list" ),
   path("delete-user/", views.delete_user, name="delete_user"),
  



    


]
