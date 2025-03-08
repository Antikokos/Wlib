from django.contrib import admin
from django.urls import path
from books import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
path('book/<str:book_id>/', views.book_detail, name='book_detail'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)