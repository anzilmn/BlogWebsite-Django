from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=200)
    user = models.OneToOneField("auth.User",on_delete=models.CASCADE)


def __str__(self):
    return self.name


class Category(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title
    

class Post(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    description = models.TextField()
    categories = models.ManyToManyField("posts.Category")  
    time_to_read = models.CharField(max_length=100)
    featured_image = models.ImageField(upload_to="posts/")

    author = models.ForeignKey("posts.Author", on_delete=models.CASCADE)
    published_date = models.DateField()
    is_draft = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)




from django.db import models
from django.contrib.auth.models import User

class PostRead(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # prevents duplicates


from django.db import models
from django.contrib.auth.models import User
from posts.models import Post  # Assuming Post is in posts.models

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # No null=True, user must be authenticated
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"{self.user.username} on {self.post.title}"



from django.db import models
from django.contrib.auth.models import User
from posts.models import Comment, Post  # Don't forget this

# models.py
class ReportMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_admin_replied = models.BooleanField(default=False)
    admin_reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 👇 ADD THIS NEW FIELD
    is_seen_by_admin = models.BooleanField(default=False)

    def __str__(self):
        comment_preview = self.comment.content if self.comment else "(Deleted)"
        post_title = self.comment.post.title if self.comment and self.comment.post else "(No Post)"
        return f"{self.user.username} reported comment: \"{comment_preview}\" on post: \"{post_title}\""






# posts/models.py

class MessageNotification(models.Model):
    post_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_notifications')
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)  # ✅ Add this field

    def __str__(self):
        return f"{self.commenter.username} commented on {self.post.title}"





# users/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    linkedin = models.URLField(blank=True)
    suspended_until = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_profile_pic_url(self):
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        return '/static/images/profile.png'

    def is_suspended(self):
        return self.suspended_until is not None and now() < self.suspended_until


