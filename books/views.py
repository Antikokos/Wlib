from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm

def home(request):
    fantasy_books = get_books_by_genre('fantasy')
    detective_books = get_books_by_genre('detective')
    manga_books = get_books_by_genre('manga')
    romance_books = get_books_by_genre('romance')

    context = {
        'fantasy_books': fantasy_books,
        'detective_books': detective_books,
        'manga_books': manga_books,
        'romance_books': romance_books,
    }
    return render(request, 'books/home.html', context)

def get_books_by_genre(genre, max_results=10):
    api_key = 'AIzaSyDz_Ps6nlxBK9ISxjSHIqMhHvjaFuq__eA'
    url = f'https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults={max_results}&key={api_key}'
    try:
        response = requests.get(url)
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
                    'thumbnail': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
                }
                books.append(book)
        return books
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return []

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
                    'id': item['id'],
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

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'books/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'books/profile.html')

def logout_view(request):
    logout(request)
    return redirect('home')