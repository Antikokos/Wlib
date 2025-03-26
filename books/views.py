from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

import requests
from .forms import RegisterForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
import json
from .models import UserBook  # Import the UserBook model

def home(request):
    return render(request, 'books/home.html')

def search(request):
    query = request.GET.get('q', '')
    if query:
        api_key = 'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA'
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
        response = requests.get(url)
        data = response.json()
        books = []
        if 'items' in data:
            for item in data['items']:
                book = {
                    'id': item['id'],  # Добавляем ID книги
                    'title': item['volumeInfo'].get('title', 'Без названия'),
                    'authors': ', '.join(item['volumeInfo'].get('authors', ['Неизвестные авторы'])),
                    'publisher': item['volumeInfo'].get('publisher', 'Не указан'),
                    'page_count': item['volumeInfo'].get('pageCount', 0),
                    'published_date': item['volumeInfo'].get('publishedDate', 'Не указан'),
                    'thumbnail': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
                }
                books.append(book)
        return render(request, 'books/search.html', {'books': books, 'query': query})
    return redirect('home')


def book_detail(request, book_id):
    api_key = 'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA'
    url = f'https://www.googleapis.com/books/v1/volumes/{book_id}?key={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        book = response.json()
        book_data = {
            'id': book['id'],
            'title': book['volumeInfo'].get('title', 'Без названия'),
            'authors': ', '.join(book['volumeInfo'].get('authors', ['Неизвестные авторы'])),
            'publisher': book['volumeInfo'].get('publisher', 'Не указан'),
            'page_count': book['volumeInfo'].get('pageCount', 0),
            'published_date': book['volumeInfo'].get('publishedDate', 'Не указан'),
            'thumbnail': book['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
            'description': book['volumeInfo'].get('description', 'Описание отсутствует'),
        }
        return render(request, 'books/book_detail.html', {'book': book_data})
    else:
        return render(request, 'books/404.html', {'message': 'Книга не найдена'})

class RegisterView(FormView):
    template_name = 'books/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)



@login_required
@csrf_protect  # Вместо @csrf_exempt, потому что @login_required уже защищает от внешних запросов
def update_book_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            book_id = data.get('book_id')
            status = data.get('status')

            if not book_id or not status:
                return JsonResponse({'success': False, 'message': 'Недостаточно данных'})

            # Получаем или создаем запись для пользователя и книги
            user_book, created = UserBook.objects.update_or_create(
                user=request.user,
                book_id=book_id,
                defaults={'status': status}
            )

            return JsonResponse({'success': True, 'message': 'Статус обновлен'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


def profile(request):
    api_key = 'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA'
    user_books = UserBook.objects.filter(user=request.user)

    books_data = []
    for user_book in user_books:
        url = f'https://www.googleapis.com/books/v1/volumes/{user_book.book_id}?key={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            book = response.json()
            book_data = {
                'id': book['id'],
                'title': book['volumeInfo'].get('title', 'Без названия'),
                'authors': ', '.join(book['volumeInfo'].get('authors', ['Неизвестные авторы'])),
                'thumbnail': book['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
                'status': user_book.status,
                'progress': user_book.progress,
            }
            books_data.append(book_data)

    # Разделяем книги по статусам
    read_books = [book for book in books_data if book['status'] == 'read']
    reading_books = [book for book in books_data if book['status'] == 'reading']
    want_to_read_books = [book for book in books_data if book['status'] == 'want-to-read']

    return render(request, 'books/profile.html', {
        'read_books': read_books,
        'reading_books': reading_books,
        'want_to_read_books': want_to_read_books,
    })

def logout_view(request):
    logout(request)
    return redirect('home')