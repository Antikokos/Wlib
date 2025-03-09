from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests

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

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Перенаправляем на главную страницу после регистрации
    else:
        form = CustomUserCreationForm()
    return render(request, 'books/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # Используем стандартную форму входа
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Перенаправляем на главную страницу
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})
@login_required
def profile_view(request):
    return render(request, 'books/profile.html')

def logout_view(request):
    logout(request)
    return redirect('home')