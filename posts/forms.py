from django import forms
from posts.models import Post
from ckeditor.widgets import CKEditorWidget  

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'class': "input"}), 
        label="Tags (Comma separated)"
    )

    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Post
        exclude = ('author', 'published_date', 'is_deleted', 'categories')
        widgets = {  
            "time_to_read": forms.TextInput(attrs={'class': "input"}),
            "title": forms.TextInput(attrs={'class': "input"}),
            "short_description": forms.Textarea(attrs={'class': "input"}),
            "featured_image": forms.FileInput(attrs={'class': "input"}),  # File Input
            "is_draft": forms.CheckboxInput(attrs={'class': "checkbox-input"}),
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:  # ✅ If editing an existing post
            if self.instance.featured_image:  # ✅ If an image is already uploaded
                self.fields['featured_image'].widget.attrs['data-current-file'] = self.instance.featured_image.url
