from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.core.cache import cache
import requests
import json
import logging
from .forms import RegisterForm
from .models import UserBook

logger = logging.getLogger(__name__)

API_KEY = 'AIzaSyBzihVeBYzNjUjj-o-7DJCucdcbgj1wuU4'
DEFAULT_BOOK_COVER = '/static/books/images/default_book_cover.jpg'
API_TIMEOUT = 10


def get_books_by_genre(genre, max_results=40):
    """Получает книги по жанру с кэшированием"""
    cache_key = f'books_{genre}_{max_results}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults={max_results}&key={API_KEY}'

    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        books = []

        if 'items' in data:
            for item in data['items']:
                book = {
                    'id': item['id'],
                    'title': item['volumeInfo'].get('title', 'Без названия'),
                    'authors': ', '.join(item['volumeInfo'].get('authors', ['Неизвестные авторы'])),
                    'publisher': item['volumeInfo'].get('publisher', 'Не указан'),
                    'page_count': item['volumeInfo'].get('pageCount', 0),
                    'published_date': item['volumeInfo'].get('publishedDate', 'Не указан'),
                    'thumbnail': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                }
                books.append(book)

        cache.set(cache_key, books, 3600)
        return books

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе книг по жанру {genre}: {e}")
        return []


def home(request):
    """Главная страница с книгами по жанрам"""
    context = {
        'fantasy_books': get_books_by_genre('fantasy'),
        'detective_books': get_books_by_genre('detective'),
        'manga_books': get_books_by_genre('manga'),
        'romance_books': get_books_by_genre('romance'),
    }
    return render(request, 'books/home.html', context)


def search(request):
    """Поиск книг"""
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('home')

    cache_key = f'search_{query}'
    cached_data = cache.get(cache_key)

    if cached_data:
        return render(request, 'books/search.html', {'books': cached_data, 'query': query})

    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}'

    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        books = []

        if 'items' in data:
            for item in data['items']:
                book = {
                    'id': item['id'],
                    'title': item['volumeInfo'].get('title', 'Без названия'),
                    'authors': ', '.join(item['volumeInfo'].get('authors', ['Неизвестные авторы'])),
                    'publisher': item['volumeInfo'].get('publisher', 'Не указан'),
                    'page_count': item['volumeInfo'].get('pageCount', 0),
                    'published_date': item['volumeInfo'].get('publishedDate', 'Не указан'),
                    'thumbnail': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                }
                books.append(book)

        cache.set(cache_key, books, 1800)
        return render(request, 'books/search.html', {'books': books, 'query': query})

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при поиске книг: {e}")
        return render(request, 'books/search.html', {'books': [], 'query': query})


def book_detail(request, book_id):
    """Детальная страница книги"""
    cache_key = f'book_{book_id}'
    cached_data = cache.get(cache_key)

    if cached_data:
        book_data = cached_data
    else:
        url = f'https://www.googleapis.com/books/v1/volumes/{book_id}?key={API_KEY}'

        try:
            response = requests.get(url, timeout=API_TIMEOUT)

            if response.status_code == 404:
                raise Http404("Книга не найдена")

            response.raise_for_status()
            book = response.json()

            book_data = {
                'id': book['id'],
                'title': book['volumeInfo'].get('title', 'Без названия'),
                'authors': ', '.join(book['volumeInfo'].get('authors', ['Неизвестные авторы'])),
                'publisher': book['volumeInfo'].get('publisher', 'Не указан'),
                'page_count': book['volumeInfo'].get('pageCount', 0),
                'published_date': book['volumeInfo'].get('publishedDate', 'Не указан'),
                'thumbnail': book['volumeInfo'].get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                'description': book['volumeInfo'].get('description', 'Описание отсутствует'),
            }

            cache.set(cache_key, book_data, 86400)
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении деталей книги {book_id}: {e}")
            raise Http404("Не удалось загрузить информацию о книге")

    # Проверяем статус книги для текущего пользователя
    user_book_data = {
        'has_book': False,
        'status': '',
        'progress': 0,
        'progress_percent': 0
    }

    if request.user.is_authenticated:
        try:
            user_book = UserBook.objects.get(user=request.user, book_id=book_id)
            user_book_data = {
                'has_book': True,
                'status': user_book.status,
                'progress': user_book.progress,
                'progress_percent': user_book.progress_percent
            }
        except UserBook.DoesNotExist:
            pass

    context = {
        'book': book_data,
        'user_book': user_book_data,
        'is_authenticated': request.user.is_authenticated
    }
    return render(request, 'books/book_detail.html', context)


class RegisterView(FormView):
    """Регистрация пользователя"""
    template_name = 'books/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@login_required
@csrf_protect
def update_progress(request):
    if request.method == "POST":
        data = json.loads(request.body)
        book_id = data.get("book_id")
        progress = data.get("progress")
        progress_percent = data.get('progress_percent', 0)

        try:
            user_book = UserBook.objects.get(user=request.user, book_id=book_id)
            user_book.progress = progress
            user_book.progress_percent = progress_percent
            user_book.save()

            # Очищаем кэш
            cache.delete(f'profile_book_{book_id}')
            cache.delete(f'book_{book_id}')

            return JsonResponse({
                "status": "success",
                "progress": progress,
                "progress_percent": progress_percent
            })
        except UserBook.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Книга не найдена в вашем списке"
            }, status=404)

    return JsonResponse({
        "status": "error",
        "message": "Неверный запрос"
    }, status=400)


@login_required
@csrf_protect
def update_book_status(request):
    """Обновление статуса книги для пользователя"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Неверный метод запроса'
        }, status=405)

    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        status = data.get('status')
        progress = data.get('progress', 0)
        progress_percent = data.get('progress_percent', 0)

        if not book_id or not status:
            return JsonResponse({
                'success': False,
                'message': 'Недостаточно данных'
            }, status=400)

        # Обновляем или создаем запись
        UserBook.objects.update_or_create(
            user=request.user,
            book_id=book_id,
            defaults={
                'status': status,
                'progress': progress,
                'progress_percent': progress_percent
            }
        )

        # Очищаем кэш
        cache.delete(f'profile_book_{book_id}')
        cache.delete(f'book_{book_id}')

        return JsonResponse({
            'success': True,
            'message': 'Статус обновлен'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Неверный формат данных'
        }, status=400)
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса книги: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Внутренняя ошибка сервера'
        }, status=500)


@login_required
@csrf_protect
def remove_book(request):
    """Удаление книги из профиля пользователя"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Неверный метод запроса'
        }, status=405)

    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')

        if not book_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан ID книги'
            }, status=400)

        # Удаляем книгу из профиля пользователя
        deleted_count, _ = UserBook.objects.filter(
            user=request.user,
            book_id=book_id
        ).delete()

        if deleted_count > 0:
            # Очищаем кэш
            cache.delete(f'profile_book_{book_id}')
            cache.delete(f'book_{book_id}')

            return JsonResponse({
                'success': True,
                'message': 'Книга удалена из профиля'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Книга не найдена в вашем профиле'
            }, status=404)

    except Exception as e:
        logger.error(f"Ошибка при удалении книги: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Ошибка при удалении'
        }, status=500)


@login_required
def get_book_status(request):
    """Получение статуса книги для текущего пользователя"""
    book_id = request.GET.get('book_id')
    if not book_id:
        return JsonResponse({'exists': False})

    try:
        user_book = UserBook.objects.get(user=request.user, book_id=book_id)
        return JsonResponse({
            'exists': True,
            'status': user_book.status,
            'progress': user_book.progress,
            'progress_percent': user_book.progress_percent
        })
    except UserBook.DoesNotExist:
        return JsonResponse({'exists': False})


@login_required
def profile(request):
    """Профиль пользователя с его книгами"""
    # Очищаем кэш профиля при загрузке
    cache_keys = [f'profile_book_{book.book_id}' for book in
                 UserBook.objects.filter(user=request.user)]
    cache.delete_many(cache_keys)

    user_books = UserBook.objects.filter(user=request.user)
    books_data = []

    for user_book in user_books:
        cache_key = f'profile_book_{user_book.book_id}'
        book_data = cache.get(cache_key)

        if not book_data:
            url = f'https://www.googleapis.com/books/v1/volumes/{user_book.book_id}?key={API_KEY}'

            try:
                response = requests.get(url, timeout=API_TIMEOUT)
                if response.status_code == 200:
                    book = response.json()
                    book_data = {
                        'id': book['id'],
                        'title': book['volumeInfo'].get('title', 'Без названия'),
                        'authors': ', '.join(book['volumeInfo'].get('authors', ['Неизвестные авторы'])),
                        'thumbnail': book['volumeInfo'].get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                        'status': user_book.status,
                        'progress': user_book.progress,
                        'progress_percent': user_book.progress_percent,
                        'page_count': book['volumeInfo'].get('pageCount', 0),  # Добавляем общее количество страниц
                    }
                    cache.set(cache_key, book_data, 86400)
            except requests.exceptions.RequestException:
                continue

        if book_data:
            books_data.append(book_data)

    # Группируем книги по статусам
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