import csv
from django.core.management.base import BaseCommand
from books.models import NewBook, NewGenre

class Command(BaseCommand):
    help = 'Импорт книг из CSV без ISBN-10'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Определяем уникальный идентификатор (используем isbn_13 если есть, иначе title + author)
                    unique_id = row.get('isbn_13') or f"{row['title']}_{row['authors']}"
                    
                    # Создаем или обновляем книгу
                    book, created = NewBook.objects.update_or_create(
                        isbn_13=row.get('isbn_13', ''),
                        defaults={
                            'title': row['title'],
                            'authors': row['authors'],
                            'publisher': row.get('publisher', ''),
                            'published_date': row.get('published_date', ''),
                            'page_count': int(row['page_count']) if row.get('page_count') else None,
                            'description': row.get('description', ''),
                            'thumbnail': row.get('thumbnail_url', ''),
                            'language': row.get('language', 'ru'),
                            'average_rating': float(row['rating']) if row.get('rating') else None,
                            # isbn_10 специально не указываем
                        }
                    )

                    # Обработка жанров
                    if 'genres' in row:
                        for genre_name in row['genres'].split('|'):
                            genre, _ = NewGenre.objects.get_or_create(
                                name=genre_name.strip(),
                                slug=genre_name.strip().lower()
                            )
                            book.genres.add(genre)

                    self.stdout.write(f'Обработано: {book.title} ({"создана" if created else "обновлена"})')

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Ошибка в строке {row}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('Импорт завершен!'))