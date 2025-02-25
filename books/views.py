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