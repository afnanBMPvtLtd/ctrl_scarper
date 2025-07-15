from django.contrib import admin
from django.urls import path
from scraper.views import scrape_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', scrape_view, name='scrape'),  # 👈 This is the homepage URL
]
