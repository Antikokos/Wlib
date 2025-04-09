from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import Q
import json
import logging
from .forms import RegisterForm
from .models import NewBook, NewUserBook, UserProfile, NewGenre

logger = logging.getLogger(__name__)

DEFAULT_BOOK_COVER = '/static/books/images/default_book_cover.jpg'

def get_books_by_genre(genre, max_results=40):
    """Получает книги по жанру из локальной базы с кэшированием"""
    cache_key = f'books_{genre}_{max_results}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return cached_data
        
    books = NewBook.objects.filter(
        genres__name__iexact=genre
    )[:max_results]
    
    book_list = []
    for book in books:
        book_list.append({
            'id': str(book.id),
            'title': book.title,
            'authors': book.authors,
            'publisher': book.publisher,
            'page_count': book.page_count,
            'published_date': book.published_date,
            'thumbnail': book.thumbnail if book.thumbnail else DEFAULT_BOOK_COVER,
        })
    
    cache.set(cache_key, book_list, 3600)
    return book_list

def home(request):
    """Главная страница с книгами по жанрам"""
    context = {
        'fantasy_books': get_books_by_genre('Фантастика'),
        'detective_books': get_books_by_genre('Детектив'),
        'manga_books': get_books_by_genre('Манга'),
        'romance_books': get_books_by_genre('Романтика'),
    }
    return render(request, 'books/home.html', context)

def search(request):
    """Поиск книг в локальной базе"""
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('home')

    cache_key = f'search_{query}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return render(request, 'books/search.html', {'books': cached_data, 'query': query})

    books = NewBook.objects.filter(
        Q(title__icontains=query) | 
        Q(authors__icontains=query)
    )[:20]
    
    book_list = []
    for book in books:
        book_list.append({
            'id': str(book.id),
            'title': book.title,
            'authors': book.authors,
            'publisher': book.publisher,
            'page_count': book.page_count,
            'published_date': book.published_date,
            'thumbnail': book.thumbnail if book.thumbnail else DEFAULT_BOOK_COVER,
        })

    cache.set(cache_key, book_list, 1800)
    return render(request, 'books/search.html', {'books': book_list, 'query': query})

def book_detail(request, book_id):
    """Детальная страница книги из локальной базы"""
    cache_key = f'book_{book_id}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return render(request, 'books/book_detail.html', {'book': cached_data})

    try:
        book = NewBook.objects.get(pk=book_id)
    except NewBook.DoesNotExist:
        raise Http404("Книга не найдена")

    book_data = {
        'id': str(book.id),
        'title': book.title,
        'authors': book.authors,
        'publisher': book.publisher,
        'page_count': book.page_count,
        'published_date': book.published_date,
        'thumbnail': book.thumbnail if book.thumbnail else DEFAULT_BOOK_COVER,
        'description': book.description or 'Описание отсутствует',
    }

    cache.set(cache_key, book_data, 86400)
    return render(request, 'books/book_detail.html', {'book': book_data})

class RegisterView(FormView):
    """Регистрация пользователя"""
    template_name = 'books/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('registration_success')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        profile = UserProfile.objects.create(user=user)
        profile.generate_confirmation_token()

        confirmation_url = self.request.build_absolute_uri(
            reverse('confirm_email', kwargs={'token': profile.confirmation_token})
        )

        send_mail(
            'Подтвердите ваш email',
            f'Пожалуйста, перейдите по ссылке для подтверждения: {confirmation_url}',
            'wlib-production@mail.ru',
            [user.email],
            fail_silently=False,
        )

        return redirect(self.get_success_url())

@login_required
@csrf_protect
def update_book_status(request):
    """Обновление статуса книги для пользователя"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)

    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        status = data.get('status')
        progress = data.get('progress', 0)

        if not book_id or not status:
            return JsonResponse({'success': False, 'message': 'Недостаточно данных'}, status=400)

        book = get_object_or_404(NewBook, pk=book_id)
        
        NewUserBook.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={'status': status, 'progress': progress}
        )

        cache.delete(f'profile_book_{book_id}')
        return JsonResponse({'success': True, 'message': 'Статус обновлен'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса книги: {e}")
        return JsonResponse({'success': False, 'message': 'Внутренняя ошибка сервера'}, status=500)

@login_required
def profile(request):
    """Профиль пользователя с его книгами"""
    user_books = NewUserBook.objects.filter(
        user=request.user
    ).select_related('book')

    books_data = []
    for user_book in user_books:
        book = user_book.book
        books_data.append({
            'id': str(book.id),
            'title': book.title,
            'authors': book.authors,
            'thumbnail': book.thumbnail if book.thumbnail else DEFAULT_BOOK_COVER,
            'status': user_book.status,
            'progress': user_book.progress,
        })

    books_by_status = {
        'read_books': [b for b in books_data if b['status'] == 'read'],
        'reading_books': [b for b in books_data if b['status'] == 'reading'],
        'want_to_read_books': [b for b in books_data if b['status'] == 'want-to-read'],
    }

    return render(request, 'books/profile.html', books_by_status)

def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('home')

def confirm_email(request, token):
    """Подтверждение email"""
    profile = get_object_or_404(UserProfile, confirmation_token=token)
    profile.email_confirmed = True
    profile.user.is_active = True
    profile.confirmation_token = None
    profile.save()
    profile.user.save()

    login(request, profile.user)
    return redirect('home')

def registration_success(request):
    """Страница успешной регистрации"""
    return render(request, 'books/registration/registration_success.html')