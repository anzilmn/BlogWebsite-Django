import json
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from posts.models import Post

def allow_self(function):
    def wrapper(request, *args, **kwargs):
        post_id = kwargs["id"]
        
        # Check if the user is an admin
        if request.user.is_superuser:
            # Admins can access any post
            return function(request, *args, **kwargs)

        # For non-admins, check if they own the post
        if not Post.objects.filter(id=post_id, author__user=request.user).exists():
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                response_data = {
                    "status": "error",
                    "title": "Unauthorized access",
                    "message": "Unauthorized access"
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                return HttpResponseRedirect(reverse("web:index"))

        return function(request, *args, **kwargs)

    return wrapper
