import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages
from django.db.models import Avg
import requests
from .forms import RegisterForm
from .models import UserBook, BookReview
import re

logger = logging.getLogger(__name__)

#reserved
# API_KEY = 'AIzaSyBzihVeBYzNjUjj-o-7DJCucdcbgj1wuU4'
API_KEY = 'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA'

DEFAULT_BOOK_COVER = '/static/books/images/default_book_cover.jpg'
API_TIMEOUT = 10


def get_books_by_genre(genre, max_results=40):
    url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults={max_results}&key={API_KEY}'
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        books = []
        if 'items' in data:
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                book = {
                    'id': item['id'],
                    'title': volume_info.get('title', 'Без названия'),
                    'authors': ', '.join(volume_info.get('authors', ['Неизвестные авторы'])),
                    'publisher': volume_info.get('publisher', 'Не указан'),
                    'page_count': volume_info.get('pageCount', 0),
                    'published_date': volume_info.get('publishedDate', 'Не указан'),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                }
                books.append(book)
        return books
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе книг по жанру {genre}: {e}")
        return []


def home(request):
    context = {
        'fantasy_books': get_books_by_genre('fantasy'),
        'detective_books': get_books_by_genre('detective'),
        'manga_books': get_books_by_genre('manga'),
        'romance_books': get_books_by_genre('romance'),
    }
    return render(request, 'books/home.html', context)


def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('home')
    try:
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&key={API_KEY}'
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        books = []
        if 'items' in data:
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                book = {
                    'id': item['id'],
                    'title': volume_info.get('title', 'Без названия'),
                    'authors': ', '.join(volume_info.get('authors', ['Неизвестные авторы'])),
                    'publisher': volume_info.get('publisher', 'Не указан'),
                    'page_count': volume_info.get('pageCount', 0),
                    'published_date': volume_info.get('publishedDate', 'Не указан'),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                }
                books.append(book)
        return render(request, 'books/search.html', {
            'books': books,
            'query': query,
            'total_books': len(books)
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при поиске книг: {e}")
        messages.error(request, 'Произошла ошибка при поиске книг')
        return redirect('home')


def book_detail(request, book_id):
    try:
        url = f'https://www.googleapis.com/books/v1/volumes/{book_id}?key={API_KEY}'
        response = requests.get(url, timeout=API_TIMEOUT)
        if response.status_code == 404:
            raise Http404("Книга не найдена")
        response.raise_for_status()
        book = response.json()
        volume_info = book.get('volumeInfo', {})

        industry_identifiers = volume_info.get('industryIdentifiers', [])
        isbn = next(
            (id['identifier'] for id in industry_identifiers
             if id['type'] in ['ISBN_10', 'ISBN_13']),
            '-'
        )

        categories = volume_info.get('categories', [])
        genre_text = 'Не указан'
        if categories:
            genres = [genre.strip() for category in categories for genre in category.split('/')]
            genres = list(set(genres))[:3]
            genre_text = ', '.join(genres) if genres else 'Не указан'

        book_data = {
            'id': book['id'],
            'title': volume_info.get('title', 'Без названия'),
            'authors': ', '.join(volume_info.get('authors', ['Неизвестные авторы'])),
            'publisher': volume_info.get('publisher', 'Не указан'),
            'page_count': volume_info.get('pageCount', 0),
            'published_date': volume_info.get('publishedDate', 'Не указан'),
            'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
            'description': volume_info.get('description', 'Описание отсутствует'),
            'language': volume_info.get('language', 'Неизвестно'),
            'rating': volume_info.get('averageRating'),
            'rating_count': volume_info.get('ratingsCount', 0),
            'genre': genre_text,
            'isbn': isbn,
            'is_readable_online': book.get('accessInfo', {}).get('webReaderLink') is not None,
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении деталей книги {book_id}: {e}")
        raise Http404("Не удалось загрузить информацию о книге")

    user_book_data = {
        'has_book': False,
        'status': '',
        'progress': 0,
        'progress_percent': 0
    }

    if request.user.is_authenticated:
        try:
            user_books = UserBook.objects.filter(user=request.user, book_id=book_id).order_by('-updated_at')
            if user_books.exists():
                user_book = user_books.first()
                user_book_data = {
                    'has_book': True,
                    'status': user_book.status,
                    'progress': user_book.progress,
                    'progress_percent': user_book.progress_percent
                }
                if user_books.count() > 1:
                    user_books.exclude(pk=user_book.pk).delete()
                    logger.warning(f"Удалены дубликаты книги {book_id} для пользователя {request.user.username}")
        except Exception as e:
            logger.error(f"Ошибка при получении данных пользователя о книге {book_id}: {e}")

    reviews = BookReview.objects.filter(book_id=book_id).select_related('user').order_by('-created_at')
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    rating_bars = []
    for stars in ['5', '4', '3', '2', '1']:
        count = reviews.filter(rating=int(stars)).count()
        percent = (count / total_reviews * 100) if total_reviews > 0 else 0
        rating_bars.append({
            'stars': stars,
            'count': count,
            'percent': round(percent, 1)
        })

    user_review = None
    if request.user.is_authenticated:
        user_review = BookReview.objects.filter(
            user=request.user,
            book_id=book_id
        ).first()

    context = {
        'book': book_data,
        'user_book': user_book_data,
        'is_authenticated': request.user.is_authenticated,
        'reviews': reviews[:10],
        'rating_bars': rating_bars,
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1) if average_rating else 0,
        'user_review': user_review,
        'user_has_reviewed': user_review is not None,
        'reviews_exist': total_reviews > 0,
    }

    return render(request, 'books/book_detail.html', context)


@login_required
@csrf_protect
def add_review(request, book_id):
    if request.method != 'POST':
        return redirect('home')

    rating = request.POST.get('rating')
    text = request.POST.get('text', '').strip()

    if not rating:
        messages.error(request, 'Необходимо указать рейтинг')
        return redirect('book_detail', book_id=book_id)

    if not text:
        messages.error(request, 'Текст отзыва не может быть пустым')
        return redirect('book_detail', book_id=book_id)

    if len(text) > 1000:
        messages.error(request, 'Текст отзыва не может превышать 1000 символов')
        return redirect('book_detail', book_id=book_id)

    try:
        BookReview.objects.update_or_create(
            user=request.user,
            book_id=book_id,
            defaults={'rating': rating, 'text': text}
        )
        messages.success(request, 'Ваш отзыв успешно сохранен!')
    except Exception as e:
        logger.error(f"Ошибка при сохранении отзыва: {e}")
        messages.error(request, 'Произошла ошибка при сохранении отзыва')

    return redirect('book_detail', book_id=book_id)

from django.contrib.auth import authenticate, login

class RegisterView(FormView):
    template_name = 'books/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('home')  # Перенаправляем на главную

    def form_valid(self, form):
        user = form.save()

        # Аутентифицируем пользователя
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=raw_password)

        if user is not None:
            login(self.request, user)  # Логиним пользователя

        return super().form_valid(form)



@login_required
@csrf_protect
def update_progress(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "message": "Неверный метод запроса"
        }, status=405)

    try:
        data = json.loads(request.body)
        book_id = data.get("book_id")
        progress = data.get("progress")
        progress_percent = data.get('progress_percent', 0)

        if not book_id or progress is None:
            return JsonResponse({
                "status": "error",
                "message": "Недостаточно данных"
            }, status=400)

        user_book = UserBook.objects.get(user=request.user, book_id=book_id)
        user_book.progress = progress
        user_book.progress_percent = progress_percent

        # Логика обновления статуса
        if progress_percent >= 100:
            user_book.status = 'read'
        elif user_book.status == 'read' and progress_percent < 100:
            # Если книга была прочитана, но прогресс уменьшили - меняем статус
            user_book.status = 'reading'

        user_book.save()
        user_book.refresh_from_db()

        return JsonResponse({
            "status": "success",
            "progress": progress,
            "progress_percent": progress_percent,
            "current_status": user_book.status
        })

    except UserBook.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Книга не найдена в вашем списке"
        }, status=404)
    except Exception as e:
        logger.error(f"Ошибка при обновлении прогресса: {e}")
        return JsonResponse({
            "status": "error",
            "message": "Внутренняя ошибка сервера"
        }, status=500)


@login_required
@csrf_protect
def update_book_status(request):
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

        UserBook.objects.update_or_create(
            user=request.user,
            book_id=book_id,
            defaults={
                'status': status,
                'progress': progress,
                'progress_percent': progress_percent
            }
        )

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

        deleted_count, _ = UserBook.objects.filter(
            user=request.user,
            book_id=book_id
        ).delete()

        if deleted_count > 0:
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
def get_books_count(request):
    try:
        counts = {
            'read': UserBook.objects.filter(user=request.user, status='read').count(),
            'reading': UserBook.objects.filter(user=request.user, status='reading').count(),
            'want-to-read': UserBook.objects.filter(user=request.user, status='want-to-read').count(),
        }
        return JsonResponse({
            'success': True,
            'counts': counts
        })
    except Exception as e:
        logger.error(f"Error getting books count: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Ошибка при получении количества книг'
        }, status=500)


@login_required
def profile(request):
    user_books = UserBook.objects.filter(user=request.user)
    books_data = []

    for user_book in user_books:
        try:
            url = f'https://www.googleapis.com/books/v1/volumes/{user_book.book_id}?key={API_KEY}'
            response = requests.get(url, timeout=API_TIMEOUT)
            if response.status_code == 200:
                book = response.json()
                volume_info = book.get('volumeInfo', {})
                book_data = {
                    'id': book['id'],
                    'title': volume_info.get('title', 'Без названия'),
                    'authors': ', '.join(volume_info.get('authors', ['Неизвестные авторы'])),
                    'thumbnail': volume_info.get('imageLinks', {}).get('thumbnail', DEFAULT_BOOK_COVER),
                    'status': user_book.status,
                    'progress': user_book.progress,
                    'progress_percent': user_book.progress_percent,
                    'page_count': volume_info.get('pageCount', 0),
                }
                books_data.append(book_data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении данных книги: {e}")
            continue

    books_by_status = {
        'read_books': [b for b in books_data if b['status'] == 'read'],
        'reading_books': [b for b in books_data if b['status'] == 'reading'],
        'want_to_read_books': [b for b in books_data if b['status'] == 'want-to-read'],
    }

    return render(request, 'books/profile.html', books_by_status)


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
@csrf_protect
def delete_review(request, review_id):
    try:
        review = BookReview.objects.get(id=review_id, user=request.user)
        review.delete()
        return JsonResponse({'success': True, 'message': 'Отзыв успешно удален'})
    except BookReview.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Отзыв не найден'}, status=404)
    except Exception as e:
        logger.error(f"Ошибка при удалении отзыва: {e}")
        return JsonResponse({'success': False, 'message': 'Ошибка при удалении отзыва'}, status=500)