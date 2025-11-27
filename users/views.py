from django.shortcuts import render, redirect,reverse
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
#from .models import CustomUser
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
#from .forms import SignupForm
from posts.models import Author
from django.shortcuts import render, redirect, get_object_or_404
from posts.models import Post, Author



def user_logout(request):
    request.session.flush()  # Clears session
    messages.success(request, "Logged out successfully!")
    return redirect("web:index")  # Redirect to homepage


 


from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from posts.models import Author  # Assuming Author is linked to User

def sign_log(request):
    signup_errors = []  # Stores signup error messages
    login_errors = []   # Stores login error messages
    success_message = None  # Message displayed after successful signup
    form_state = "signup"  # Default form state

    if request.method == "POST":
        action = request.POST.get("action")  # Check if user is signing up or logging in

        # ✅ SIGNUP LOGIC
        if action == "signup":
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            # 🚨 Basic validation checks
            if not username or not email or not password or not confirm_password:
                signup_errors.append("All fields are required!")

            if User.objects.filter(username=username).exists():
                signup_errors.append("Username already exists!")
            if User.objects.filter(email=email).exists():
                signup_errors.append("Email already registered!")

            if len(password) < 8:
                signup_errors.append("Password must be at least 8 characters long!")

            if password != confirm_password:
                signup_errors.append("Passwords do not match!")

            # ✅ If no errors, create the user in Django’s `User` model
            if not signup_errors:
                user = User.objects.create_user(username=username, email=email, password=password)

                # ✅ Automatically create an Author profile for the new user
                Author.objects.create(name=username, user=user)

                success_message = "Signup successful! You can log in now."
                form_state = "login"  # Switch form to login mode

        # ✅ LOGIN LOGIC
        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")

            if not username or not password:
                login_errors.append("All fields are required!")
            else:
                user = authenticate(request, username=username, password=password)

                if user is not None:
                    auth_login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect("web:index")  # ✅ Redirect to homepage
                else:
                    login_errors.append("Invalid username or password!")

            form_state = "login"

    # ✅ Render the login/signup page
    return render(request, "users/sign_log.html", {
        "signup_errors": signup_errors,
        "login_errors": login_errors,
        "success_message": success_message,
        "form_state": form_state
    })





from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from posts.models import Author, Post

@login_required
def users_list(request):
    users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)

    users_with_post_count = []
    for user in users:
        try:
            author_instance = Author.objects.get(user=user)  # Get Author linked to User
            post_count = Post.objects.filter(author=author_instance).count()
        except Author.DoesNotExist:
            post_count = 0  # If no Author instance exists, set post count to 0

        users_with_post_count.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,  # ✅ Added email here
            "post_count": post_count,
        })

    return render(request, "users/users_list.html", {"users": users_with_post_count})




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from posts.models import Post, Category, Author
import json
from django.db import transaction

@login_required(login_url="/users/sign_log/")
def delete_user(request):
    if request.method == "POST":
        try:
            # Get user_id from the request body
            data = json.loads(request.body)
            user_id = data.get("user_id")

            # Ensure the user exists
            user = get_object_or_404(User, id=user_id)

            if request.user.is_superuser:  # Only admin can delete
                # Start a transaction to ensure atomic operations
                with transaction.atomic():
                    # Fetch the author associated with the user (if it exists)
                    author = Author.objects.filter(user=user).first()

                    # Fetch all the posts by this user
                    posts = Post.objects.filter(author__user=user)

                    # Delete associated categories if they are not used by other posts
                    for post in posts:
                        for category in post.categories.all():
                            if category.post_set.count() == 1:  # Check if no other posts are using this category
                                category.delete()  # Delete category if it's not used by any other post
                        post.delete()  # Delete the post itself
                    
                    # Now, delete the author (if it exists) to ensure no orphaned data
                    if author:
                        author.delete()

                    # Now, delete the user from the auth model
                    user.delete()
                
                return JsonResponse({"status": "success", "message": "User and their posts deleted successfully!"})
            
            else:
                return JsonResponse({"status": "error", "message": "Permission denied!"}, status=403)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)














