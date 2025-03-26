// Пагинация - Показать еще
document.addEventListener("DOMContentLoaded", function() {
    const loadMoreBtn = document.getElementById('load-more');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            const hiddenBooks = document.getElementById('hidden-books');
            const bookContainer = document.getElementById('book-container');
            const booksCount = document.getElementById('books-count');
            
            // Берем первые 10 скрытых книг
            const booksToShow = Array.from(hiddenBooks.children).slice(0, 10);
            
            if (booksToShow.length > 0) {
                // Добавляем их в основной контейнер
                booksToShow.forEach(book => {
                    bookContainer.appendChild(book);
                });
                
                // Обновляем счетчик
                const currentShown = bookContainer.children.length;
                const totalBooks = parseInt('{{ total_books }}');
                booksCount.textContent = `${currentShown}/40`;
                
                // Если больше нечего показывать - скрываем кнопку
                if (hiddenBooks.children.length === 0) {
                    loadMoreBtn.style.display = 'none';
                }
            }
        });
    }
    
    // Остальной ваш код...
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.book-info p').forEach(p => {
        if (p.textContent.includes("Год выхода:")) {
            let yearMatch = p.textContent.match(/\d{4}/); // Ищем 4 цифры подряд (год)
            if (yearMatch) {
                p.innerHTML = `<span class="bold-text">Год выхода:</span> ${yearMatch[0]}`; // Добавляем класс к "Год выхода:"
            }
        }
    });
});



function getTextValue(book, keyword) {
    const textElement = [...book.querySelectorAll('.book-info p')]
        .find(p => p.textContent.includes(keyword));

    if (!textElement) {
        console.warn(`Не найдено поле "${keyword}" в`, book);
        return 0;
    }

    let value = textElement.textContent.replace(/\D/g, ''); // Оставляем только цифры

    if (keyword === "Год выхода") {
        if (value.length >= 8) {
            // Если полный формат "YYYY-MM-DD", возвращаем как дату
            return new Date(value.slice(0, 4), value.slice(4, 6) - 1, value.slice(6, 8)).getTime();
        } else if (value.length === 4) {
            // Если только год "YYYY", возвращаем число
            return parseInt(value, 10);
        }
    }

    return parseInt(value, 10) || 0; // Для страниц и других чисел
}

function getTextValue(book, keyword) {
    const textElement = [...book.querySelectorAll('.book-info p')]
        .find(p => p.textContent.includes(keyword));

    return textElement ? parseInt(textElement.textContent.replace(/\D/g, ''), 10) : 0;
}

function sortBooks() {
    const sortOption = document.getElementById("sortOption").value;
    const books = Array.from(document.querySelectorAll('.book-container a')); // Берем <a>, а не .book-card

    books.sort((a, b) => {
        if (sortOption === "pages") {
            return getTextValue(b, "Кол-во страниц") - getTextValue(a, "Кол-во страниц");
        } else if (sortOption === "year") {
            return getTextValue(b, "Год выхода") - getTextValue(a, "Год выхода"); // Сортировка по году
        }
    });

    const bookContainer = document.getElementById('book-container');
    bookContainer.append(...books); // Оптимизированное добавление
}


let isReversed = false;

function reverseBooks() {
    isReversed = !isReversed; // Переключаем флаг реверса
    const bookContainer = document.getElementById('book-container');
    const books = Array.from(bookContainer.children).reverse();
    
    updateBookList(books);

    // Добавляем/убираем класс поворота
    document.querySelector('.reverse-button').classList.toggle('rotated', isReversed);
}

function updateBookList(books) {
    const bookContainer = document.getElementById('book-container');
    const fragment = document.createDocumentFragment();

    books.forEach(book => fragment.appendChild(book));
    
    bookContainer.innerHTML = ''; 
    bookContainer.appendChild(fragment);
}
