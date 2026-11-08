from django.db import models
from django.contrib.auth.models import User

STATUS = (
    (0, "Private"),
    (1, "Public")
)

# Create your models here.

class Recipe(models.Model):
    title = models.CharField(max_length=254)
    slug = models.SlugField(max_length=254, unique=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    is_public = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS, default=0)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on', '-updated_on']

    def __str__(self):
        return f"{self.title} by {self.author}"