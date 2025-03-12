from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from books import views
from books.views import RegisterView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('book/<str:book_id>/', views.book_detail, name='book_detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)