from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from books import views
from books.views import RegisterView, update_progress


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('book/<str:book_id>/', views.book_detail, name='book_detail'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('update_book_status/', views.update_book_status, name='update_book_status'),
    path("update-progress/", update_progress, name="update_progress"),
    path('get_book_status/', views.get_book_status, name='get_book_status'),
    path('remove_book/', views.remove_book, name='remove_book'),
path('book/<str:book_id>/add_review/', views.add_review, name='add_review'),
path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)