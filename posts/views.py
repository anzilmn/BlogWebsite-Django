from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from posts.forms import PostForm
from django.http import HttpResponse
import json
import datetime
from posts.models import Author, Category, Post
from main.decorators import allow_self
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
import datetime
from posts.models import Author, Category
from .forms import PostForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from posts.models import Author, Category, Post
from posts.models import Profile  # make sure you import Profile
import datetime
from .forms import PostForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from posts.forms import PostForm
from posts.models import Author, Post, Category
from posts.models import Profile  # make sure you import this
import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.timezone import now
from posts.models import Post, Author, Category
from posts.forms import PostForm
import datetime

@login_required(login_url="/users/sign_log/")
def create_post(request):
    # Ensure latest profile state is fetched
    request.user.refresh_from_db()

    # Get or create profile
    profile = getattr(request.user, 'profile', None)
    if profile is None:
        from posts.models import Profile
        profile = Profile.objects.create(user=request.user)

    # 🛑 Check if user is suspended
    if profile.is_suspended():
        return render(request, 'users/suspended.html', {
            'message': f'🚫 Your account is suspended until {profile.suspended_until.strftime("%Y-%m-%d %H:%M")}.'
        })

    form = PostForm()

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            tags = form.cleaned_data['tags']
            author, created = Author.objects.get_or_create(user=request.user)

            instance = form.save(commit=False)
            instance.published_date = datetime.date.today()
            instance.author = author
            instance.save()

            tags_list = tags.split(",")
            for tag in tags_list:
                category, _ = Category.objects.get_or_create(title=tag.strip())
                instance.categories.add(category)

            return redirect("web:index")
    else:
        # optional pre-fill
        data = {
            "title": "World Of Anime",
            "description": "Bleach thousand blood year war arc",
            "short_description": "Kurosaki ichigo",
            "time_to_read": "8 min",
            "tags": "White,shinigami,quincy"
        }
        form = PostForm(initial=data)

    context = {
        "title": "Create new post",
        "form": form
    }

    return render(request, "posts/create.html", context)







@login_required(login_url="/users/sign_log/")
def my_posts(request):
    posts = Post.objects.filter(author=request.user.author, is_deleted=False)

    for post in posts:
        post.read_count = post.reads.count()  # 👈 Now works because of related_name="reads"

    instances = Paginator(posts, 4)
    page = request.GET.get('page', 1)

    try:
        instances = instances.page(page)
    except PageNotAnInteger:
        instances = instances.page(1)
    except EmptyPage:
        instances = instances.page(instances.num_pages)

    context = {
        "title": "My Posts",
        "instances": instances,
    }
    return render(request, "posts/my-posts.html", context)




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from posts.models import Post, Category

@login_required(login_url="/users/sign_log/")
@allow_self
def delete_post(request, id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if AJAX request
        try:
            with transaction.atomic():  # Ensure atomicity of the transaction
                # Fetch the post to be deleted
                post = get_object_or_404(Post, id=id)

                # Delete associated categories if they are not used by other posts
                for category in post.categories.all():
                    if category.post_set.count() == 1:  # Check if no other posts are using this category
                        category.delete()  # Delete the category if it's not used by any other post

                # Now delete the post from the database
                post.delete()

                return JsonResponse({"status": "success", "message": "Post and associated categories deleted successfully!"})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required(login_url="/users/sign_log/")
@allow_self
def draft_post(request, id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Check if AJAX request
        instances = get_object_or_404(Post, id=id)
        instances.is_draft = not instances.is_draft
        instances.save()

        return JsonResponse({"status": "success", "message": "Post updated successfully!"})

    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)




    
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

@login_required(login_url="/users/sign_log/")
@allow_self
def edit_post(request, id):
    instance = get_object_or_404(Post, id=id)
    page = request.GET.get('page', 1)  # Get the current page number

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            instance = form.save(commit=False)

            # ✅ Do NOT change the published_date, keep the original one
            if not instance.published_date:
                instance.published_date = datetime.date.today()  

            # ✅ Ensure the author remains the same
            if not instance.author:
                instance.author, _ = Author.objects.get_or_create(user=request.user)

            # ✅ Keep the existing image if no new one is uploaded
            if "featured_image" not in request.FILES:
                instance.featured_image = Post.objects.get(id=id).featured_image

            instance.save()

            # ✅ Update categories
            instance.categories.clear()
            tags_list = form.cleaned_data['tags'].split(",")
            for tag in tags_list:
                category, _ = Category.objects.get_or_create(title=tag.strip())
                instance.categories.add(category)

            # ✅ Set a Django success message
            messages.success(request, "✅ Post successfully edited!")

            # ✅ Redirect to the same page with 'edited' parameter
            return redirect(f"{reverse('posts:my_posts')}?page={page}&edited=true")

    else:
        category_string = ", ".join([cat.title for cat in instance.categories.all()])
        form = PostForm(instance=instance, initial={"tags": category_string})

    context = {
        "title": "Edit Post",
        "form": form,
    }
    return render(request, "posts/create.html", context)



from django.shortcuts import render, get_object_or_404
from posts.models import Post, Author
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

@login_required
def admin_user_posts(request, user_id):
    # Get the Author instance using the user_id
    author = get_object_or_404(Author, user_id=user_id)
    
    # Filter posts by the author and only non-deleted posts
    posts = Post.objects.filter(author=author, is_deleted=False)
    
    # Paginate the results
    instances = Paginator(posts, 6)
    page = request.GET.get('page', 1)
    
    try:
        instances = instances.page(page)
    except PageNotAnInteger:
        instances = instances.page(1)
    except EmptyPage:
        instances = instances.page(instances.num_pages)
    
    context = {
        "title": f"{author.name}'s Posts",  # Use author's name for the title
        "instances": instances,
        "user": author.user,  # Pass the associated User instance to the template
    }
    
    return render(request, "posts/admin_user_posts.html", context)



from posts.models import Profile, Post, Author

def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    try:
        author = Author.objects.get(user=request.user)
        post_count = Post.objects.filter(author=author).count()
    except Author.DoesNotExist:
        post_count = 0

    if request.method == 'POST':
        profile.bio = request.POST.get('bio')
        profile.location = request.POST.get('location')
        profile.website = request.POST.get('website')
        profile.twitter = request.POST.get('twitter')
        profile.linkedin = request.POST.get('linkedin')

        # ✅ Add this line to handle profile picture update
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

        profile.save()
        return redirect('posts:profile')

    return render(request, 'users/profile.html', {
        'user': request.user,
        'profile': profile,
        'post_count': post_count,
    })




# users/views.py
from django.contrib.admin.views.decorators import staff_member_required
from posts.models import Profile
@staff_member_required
def manage_suspensions(request):
    profiles = Profile.objects.filter(user__is_staff=False)  # exclude admin/staff
    return render(request, 'users/manage_suspensions.html', {'profiles': profiles})



# users/views.py
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@staff_member_required
def suspend_user(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    profile.suspended_until = now() + timedelta(days=7)
    profile.save()
    messages.success(request, f'{profile.user.username} has been suspended for 7 days.')
    return redirect('posts:manage_suspensions')

@staff_member_required
def unsuspend_user(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    profile.suspended_until = None
    profile.save()
    messages.success(request, f'{profile.user.username} has been unsuspended.')
    return redirect('posts:manage_suspensions')

