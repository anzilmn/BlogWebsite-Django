from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from posts.models import Post, Category, Author

def index(request):
    posts = Post.objects.filter(is_deleted=False, is_draft=False).order_by("-published_date").distinct()

    categories = Category.objects.all()[:12]  # nthoram tag venam enn
    authors = Author.objects.all()  # [:3] nthoram authors venaam enn

    q = request.GET.get('q')
    if q:
        posts = posts.filter(title__icontains=q).distinct()

    search_authors = request.GET.getlist("author")
    print(search_authors)

    if search_authors:
        posts = posts.filter(author__in=search_authors).distinct()

    search_categories = request.GET.getlist("category")
    print(search_categories)

    if search_categories:
        posts = posts.filter(categories__in=search_categories).distinct()

    sort = request.GET.get("sort")
    if sort:
        if sort == "title-asc":
            posts = posts.order_by("title").distinct()
        elif sort == "title-desc":
            posts = posts.order_by("-title").distinct()
        elif sort == "date-asc":
            posts = posts.order_by("published_date").distinct()
        elif sort == "date-desc":
            posts = posts.order_by("-published_date").distinct()

    instances = Paginator(posts, 6)  # post nthoram venam enn
    page = request.GET.get('page', 1)

    try:
        instances = instances.page(page)
    except PageNotAnInteger:
        instances = instances.page(1)
    except EmptyPage:
        instances = instances.page(instances.num_pages)

    context = {
        "title": "Home Page",
        "instances": instances,
        "categories": categories,
        "authors": authors
    }

    return render(request, 'web/index.html', context=context)




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from posts.models import Post, PostRead, Comment, MessageNotification
from django.utils.timezone import now

def post(request, id):
    instance = get_object_or_404(Post.objects.filter(id=id))

    is_other_user = (
        request.user.is_authenticated and
        not request.user.is_superuser and
        request.user != instance.author.user
    )

    # ✅ Track post view only if user is not admin and not the author
    if is_other_user:
        PostRead.objects.get_or_create(post=instance, user=request.user)

    # ✅ Handle comment only if user is not admin and not the author
    if request.method == "POST" and is_other_user:
        comment = request.POST.get("comment")
        if comment:
            new_comment = Comment.objects.create(
                post=instance,
                user=request.user,
                content=comment,
                created_at=now()
            )

            # ✅ Send notification to post owner
            MessageNotification.objects.create(
                post_owner=instance.author.user,
                commenter=request.user,
                post=instance,
                comment=new_comment
            )

            request.session["comment_success"] = True
            return redirect("web:post", id=instance.id)

    # ✅ Only clear it after passing to template
    comment_success = request.session.pop("comment_success", False)

    comments = instance.comments.all().order_by('-created_at')

    context = {
        "instance": instance,
        "comments": comments,
        "comment_success": comment_success
    }
    return render(request, 'web/post.html', context=context)








# views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from posts.models import Comment

@login_required
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)

    # Allow only the comment's author to delete it
    if request.user == comment.user:
        comment.delete()  # Delete the comment
    
        # Respond with success message
        return JsonResponse({'success': True})
    
    # If the user is not the comment owner, return failure
    return JsonResponse({'success': False, 'message': 'You are not authorized to delete this comment.'})



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from posts.models import Comment, Post, MessageNotification  # ✅ Import MessageNotification
from django.utils.timezone import now

# Add comment view (AJAX)
def add_ajax_comment(request):
    if request.method == 'POST' and request.user.is_authenticated:
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')

        # Ensure the post exists
        post = get_object_or_404(Post, id=post_id)

        # Create the new comment
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=comment_text,
            created_at=now()
        )

        # ✅ Create a message notification (if commenter is not post author)
        if post.author.user != request.user:
            MessageNotification.objects.create(
                post_owner=post.author.user,
                commenter=request.user,
                post=post,
                comment=comment
            )

        # Return the response with the new comment's details
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'comment_text': comment.content,
            'username': comment.user.username,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# Delete comment view (AJAX)
def delete_ajax_comment(request, comment_id):
    if request.method == 'POST' and request.user.is_authenticated:
        # Ensure the comment exists
        comment = get_object_or_404(Comment, id=comment_id)

        # Check if the user is authorized to delete the comment (either the author or admin)
        if comment.user == request.user or request.user.is_staff:
            comment.delete()
            return JsonResponse({'success': True, 'message': 'Comment deleted successfully'})
        else:
            return JsonResponse({'success': False, 'error': 'Permission denied'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})




# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from posts.models import ReportMessage
from posts.models import Comment

@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Only allow post owner to report
    if request.user == comment.post.author.user:
        if request.method == 'POST':
            message_content = request.POST.get('message')

            # Create the report message
            ReportMessage.objects.create(
                user=request.user,
                comment=comment,
                message=message_content
            )

            return redirect('web:post', id=comment.post.id)  # Redirect back to the post's detail page

        return render(request, 'web/report_comment.html', {'comment': comment})

    # If not post owner, redirect back
    return redirect('web:post', id=comment.post.id)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from posts.models import ReportMessage

@login_required
def my_reports(request):
    reports = ReportMessage.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'web/my_reports.html', {'reports': reports})




# views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from posts.models import MessageNotification

@login_required
def notifications_view(request):
    notifications = MessageNotification.objects.filter(post_owner=request.user).order_by('-created_at')

    # ✅ Mark all as seen when visiting the page
    MessageNotification.objects.filter(post_owner=request.user, seen=False).update(seen=True)

    return render(request, 'web/message.html', {'notifications': notifications})


 



from django.contrib.auth.decorators import login_required
from posts.models import MessageNotification
from django.shortcuts import redirect

@login_required
def delete_all_notifications(request):
    if request.method == 'POST':
        MessageNotification.objects.filter(post_owner=request.user).delete()
    return redirect('web:messages')  # Replace 'web:messages' with your actual URL name



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from posts.models import ReportMessage

@login_required
def delete_all_reports(request):
    if request.method == 'POST':
        ReportMessage.objects.filter(user=request.user).delete()
    return redirect('web:my_reports')


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from posts.models import ReportMessage

@staff_member_required
def report_messages_admin_view(request):
    reports = ReportMessage.objects.all().order_by('-created_at')
    return render(request, 'web/reported_messages.html', {'reports': reports})


from django.shortcuts import render, get_object_or_404, redirect
from posts.models import ReportMessage
from django.contrib.auth.decorators import login_required, user_passes_test

@user_passes_test(lambda u: u.is_superuser)
def edit_report_message(request, report_id):
    report = get_object_or_404(ReportMessage, id=report_id)
    
    if request.method == 'POST':
        report.admin_reply = request.POST.get('admin_reply', '')
        report.is_admin_replied = bool(report.admin_reply.strip())  # ✅ Set True if reply exists
        report.is_seen_by_admin = True  # Optional: mark as seen by admin
        report.save()
        return redirect('web:admin_reports')

    return render(request, 'web/edit_report_message.html', {'report': report})




