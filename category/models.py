from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=100, unique=True) # url of the category
    description = models.TextField(max_length=255, blank=True)
    image = models.ImageField(upload_to='photos/categories/', blank=True)

    # to change the "Categorys" in admin side panel:
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def _str__(self):
        return self.name