from django.contrib import admin
from posts.models import Author, Category, Post, Comment

class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "user")

admin.site.register(Author)

admin.site.register(Category)

class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_date", "short_description")

admin.site.register(Post, PostAdmin)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')  # Specify fields to display in list view
    search_fields = ('content', 'user__username')  # Make content and user searchable
    list_filter = ('created_at', 'post')  # Add filtering options

    # Add delete_comments action to delete selected comments
    actions = ['delete_comments']

    def delete_comments(self, request, queryset):
        """Allow admins to delete selected comments."""
        queryset.delete()
        self.message_user(request, "Selected comments were deleted successfully.")
    delete_comments.short_description = "Delete selected comments"

# Register the Comment model with custom options
admin.site.register(Comment, CommentAdmin)






from django.contrib import admin
from django.utils.html import format_html
from posts.models import ReportMessage

class ReportMessageAdmin(admin.ModelAdmin):
    list_display = (
        'post_title',            # 1. Blog Post Title
        'comment_text',          # 2. Comment
        'comment_author',        # 3. Comment Author
        'reported_by_user',      # 4. Reported By (Post owner)
        'report_message',        # 5. Message
        'admin_reply_status',    # 6. Admin Replied ✔️/❌
        'created_at',            # 7. Created at
    )
    readonly_fields = ('comment_text', 'post_title')

    def comment_text(self, obj):
        return obj.comment.content if obj.comment else '(Deleted)'
    comment_text.short_description = "Comment "

    def comment_author(self, obj):
        return obj.comment.user.username if obj.comment and obj.comment.user else '(Unknown)'
    comment_author.short_description = "Comment Author (Owner)"

    def post_title(self, obj):
        return obj.comment.post.title if obj.comment and obj.comment.post else '(No Post)'
    post_title.short_description = "Blog Post Title"

    def reported_by_user(self, obj):
        return obj.user.username
    reported_by_user.short_description = "Reported By (Post owner)"

    def report_message(self, obj):
        return obj.message
    report_message.short_description = "Message From Post owner"

    def admin_reply_status(self, obj):
        return format_html('<span style="color:green;">✔️</span>') if obj.admin_reply else format_html('<span style="color:red;">❌</span>')
    admin_reply_status.short_description = "Admin Replied"

admin.site.register(ReportMessage, ReportMessageAdmin)




from django.contrib import admin
from posts.models import Profile
from django.utils.timezone import now
from datetime import timedelta

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_currently_suspended', 'suspended_until')
    actions = ['suspend_1_day', 'suspend_1_week', 'unsuspend_users']

    def is_currently_suspended(self, obj):
        return obj.is_suspended()
    is_currently_suspended.boolean = True
    is_currently_suspended.short_description = "Suspended?"

    def suspend_1_day(self, request, queryset):
        until = now() + timedelta(days=1)
        queryset.update(suspended_until=until)
        self.message_user(request, "Selected users suspended for 1 day.")

    def suspend_1_week(self, request, queryset):
        until = now() + timedelta(weeks=1)
        queryset.update(suspended_until=until)
        self.message_user(request, "Selected users suspended for 1 week.")

    def unsuspend_users(self, request, queryset):
        queryset.update(suspended_until=None)
        self.message_user(request, "Selected users are now unsuspended.")

admin.site.register(Profile, ProfileAdmin)
