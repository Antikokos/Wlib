from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator

import requests
import json
import random
import logging

from .forms import RegisterForm
from .models import UserBook

logger = logging.getLogger(__name__)

# Настройки API (лучше вынести в settings.py)
API_KEYS = [
    'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA',
    'AIzaSyBQ3aJhA7Q5hZ5Q5hZ5Q5hZ5Q5hZ5Q5hZ5',
    'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eB',
    'AIzaSyBzihVeBYzNjUjj-o-7DJCucdcbgj1wuU4'
]
DEFAULT_BOOK_COVER = '/static/books/images/default_book_cover.jpg'
API_TIMEOUT = 10  # секунд
CACHE_TIMEOUT = 86400  # 24 часа для кэша


def get_api_key():
    """Возвращает случайный рабочий API ключ"""
    for key in random.sample(API_KEYS, len(API_KEYS)):
        # Простая проверка ключа (можно расширить)
        test_url = f'https://www.googleapis.com/books/v1/volumes?q=test&maxResults=1&key={key}'
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                return key
        except requests.RequestException:
            continue
    return None  # Если ни один ключ не работает


def fetch_book_data(book_id):
    """Получает данные книги из API с обработкой ошибок"""
    api_key = get_api_key()
    if not api_key:
        logger.error("No working API keys available")
        return None

    url = f'https://www.googleapis.com/books/v1/volumes/{book_id}?key={api_key}'
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            logger.info(f"Book not found: {book_id}")
        else:
            logger.warning(f"API error for book {book_id}: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for book {book_id}: {e}")
    return None


def parse_book_data(book_json, book_id):
    """Парсит данные книги из JSON ответа"""
    if not book_json:
        return None

    volume_info = book_json.get('volumeInfo', {})
    return {
        'id': book_id,
        'title': volume_info.get('title', 'Без названия'),
        'authors': ', '.join(volume_info.get('authors', ['Неизвестные авторы'])),
        'publisher': volume_info.get('publisher', 'Не указан'),
        'page_count': volume_info.get('pageCount', 0),
        'published_date': volume_info.get('publishedDate', 'Не указан'),
        'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
        'description': volume_info.get('description', 'Описание отсутствует'),
    }


def home(request):
    """Главная страница с книгами по жанрам"""
    genres = {
        'fantasy_books': 'fantasy',
        'detective_books': 'detective',
        'manga_books': 'manga',
        'romance_books': 'romance'
    }

    context = {}
    for key, genre in genres.items():
        cache_key = f'home_{genre}_books'
        books = cache.get(cache_key)

        if not books:
            books = []
            api_key = get_api_key()
            if api_key:
                url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults=40&key={api_key}'
                try:
                    response = requests.get(url, timeout=API_TIMEOUT)
                    if response.status_code == 200:
                        data = response.json()
                        books = [
                            parse_book_data(item, item['id'])
                            for item in data.get('items', [])
                            if parse_book_data(item, item['id'])
                        ]
                        cache.set(cache_key, books, CACHE_TIMEOUT)
                except requests.RequestException as e:
                    logger.error(f"Error fetching {genre} books: {e}")

        context[key] = books or []

    return render(request, 'books/home.html', context)


def search(request):
    """Поиск книг"""
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('home')

    cache_key = f'search_{query}'
    books = cache.get(cache_key)

    if books is None:
        books = []
        api_key = get_api_key()
        if api_key:
            url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
            try:
                response = requests.get(url, timeout=API_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    books = [
                        parse_book_data(item, item['id'])
                        for item in data.get('items', [])
                        if parse_book_data(item, item['id'])
                    ]
                    cache.set(cache_key, books, 1800)  # 30 минут кэша
            except requests.RequestException as e:
                logger.error(f"Search error for '{query}': {e}")

    return render(request, 'books/search.html', {
        'books': books,
        'query': query,
        'no_results': not books
    })


def book_detail(request, book_id):
    """Детальная страница книги"""
    cache_key = f'book_{book_id}'
    book = cache.get(cache_key)

    if not book:
        book_json = fetch_book_data(book_id)
        book = parse_book_data(book_json, book_id)

        if book:
            cache.set(cache_key, book, CACHE_TIMEOUT)
        else:
            # Резервный вариант - минимальные данные о книге
            book = {
                'id': book_id,
                'title': 'Информация о книге временно недоступна',
                'authors': 'Неизвестные авторы',
                'publisher': 'Не указан',
                'page_count': 0,
                'published_date': 'Не указан',
                'thumbnail': DEFAULT_BOOK_COVER,
                'description': 'Приносим извинения, но в данный момент мы не можем загрузить информацию об этой книге. Пожалуйста, попробуйте позже.',
            }
            return render(request, 'books/book_detail.html', {'book': book}, status=503)

    return render(request, 'books/book_detail.html', {'book': book})


@method_decorator(csrf_protect, name='dispatch')
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
def update_book_status(request):
    """Обновление статуса книги для пользователя"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Метод не разрешен'}, status=405)

    try:
        data = json.loads(request.body)
        book_id = data.get('book_id')
        status = data.get('status')
        progress = data.get('progress', 0)

        if not book_id or not status:
            return JsonResponse({'success': False, 'message': 'Недостаточно данных'}, status=400)

        UserBook.objects.update_or_create(
            user=request.user,
            book_id=book_id,
            defaults={'status': status, 'progress': progress}
        )
        return JsonResponse({'success': True, 'message': 'Статус обновлен'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Неверный формат данных'}, status=400)
    except Exception as e:
        logger.error(f"Error updating book status: {e}")
        return JsonResponse({'success': False, 'message': 'Внутренняя ошибка сервера'}, status=500)


@login_required
def profile(request):
    """Профиль пользователя с его книгами"""
    user_books = UserBook.objects.filter(user=request.user)

    books_data = []
    for user_book in user_books:
        book_data = cache.get(f'profile_book_{user_book.book_id}')

        if not book_data:
            book_json = fetch_book_data(user_book.book_id)
            book_data = parse_book_data(book_json, user_book.book_id)

            if book_data:
                book_data.update({
                    'status': user_book.status,
                    'progress': user_book.progress
                })
                cache.set(f'profile_book_{user_book.book_id}', book_data, CACHE_TIMEOUT)

        if book_data:
            books_data.append(book_data)

    # Группировка по статусам
    status_groups = {
        'read': [b for b in books_data if b['status'] == 'read'],
        'reading': [b for b in books_data if b['status'] == 'reading'],
        'want_to_read': [b for b in books_data if b['status'] == 'want-to-read'],
    }

    return render(request, 'books/profile.html', status_groups)


def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('home')