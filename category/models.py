from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    """
    A "slug" is a way of generating a valid URL, generally using data already obtained.

    An example:
    <title> The 46 Year Old Virgin </title>
    <slug> the-46-year-old-virgin </slug>
    """
    slug = models.SlugField(max_length=100, unique=True) # url of the category
    description = models.TextField(max_length=255, blank=True)
    image = models.ImageField(upload_to='photos/categories/', blank=True)

    # to change the "Categorys" in admin side panel:
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # this is used in navbar.html, for the category menu 
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.name