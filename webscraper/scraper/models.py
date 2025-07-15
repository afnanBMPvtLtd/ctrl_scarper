from django.db import models

class ScrapedResult(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=300, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    links = models.TextField(blank=True, null=True)  # Store as comma-separated string
    images = models.TextField(blank=True, null=True)  # Store as comma-separated string
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
