from django.db import models
from django.utils.html import strip_tags
import markdown


class Category(models.Model):
    name = models.CharField(max_length=128, default="category", unique=True, verbose_name="category name")
    post_number = models.IntegerField(default=0, verbose_name='post number')

    def increase_number(self):
        self.post_number += 1
        self.save(update_fields=['post_number'])

    def decrease_number(self):
        self.post_number -= 1
        self.save(update_fields=['post_number'])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'category'


class Tag(models.Model):
    name = models.CharField(max_length=128, default="tag", unique=True, verbose_name="tag name")

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=128, default="title", unique=True, verbose_name="post title")
    body = models.TextField()

    created_time = models.DateTimeField(verbose_name="post created time")
    modified_time = models.DateTimeField(verbose_name="post modified time")

    excerpt = models.CharField(max_length=256, blank=True)

    views = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, verbose_name='post category')
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        if not self.excerpt:
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            self.excerpt = strip_tags(md.convert(self.body))[:64]
        super(Post, self).save(*args, **kwargs)


