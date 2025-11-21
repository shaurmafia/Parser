import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import os


class PedagogyParser:
    """
    Парсер для извлечения информации о статьях с сайта pedsovet.org
    """
    
    def __init__(self, base_url="https://pedsovet.org"):
        """
        Инициализация парсера
        
        Args:
            base_url (str): Базовый URL сайта для обработки относительных ссылок
        """
        self.base_url = base_url
        self.session = requests.Session()
        # Устанавливаем заголовки, чтобы имитировать реального пользователя
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page_content(self, url):
        """
        Получает содержимое страницы по URL
        
        Args:
            url (str): URL страницы для парсинга
            
        Returns:
            BeautifulSoup object: Объект для парсинга HTML
        """
        try:
            print(f"Получаем данные с {url}...")
            response = self.session.get(url)
            response.raise_for_status()  # Проверяем успешность запроса
            
            # Создаем объект BeautifulSoup для парсинга
            soup = BeautifulSoup(response.content, 'html.parser')
            print("Страница успешно загружена")
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return None
    
    def find_article_cards(self, soup):
        """
        Находит карточки со статьями на странице
        
        Args:
            soup (BeautifulSoup): Объект для парсинга HTML
            
        Returns:
            list: Список найденных карточек статей
        """
        print("Ищем карточки статей...")
        
        # Ищем карточки статей по CSS-селекторам
        # Эти селекторы нужно уточнить через Inspect в браузере
        possible_selectors = [
            '.article-card',  # По классу карточки статьи
            '.news-item',     # По классу новостного элемента
            '.item',          # Общий класс элемента
            '.card',          # Карточка
            '[class*="article"]',  # Класс содержащий "article"
            '[class*="news"]',     # Класс содержащий "news"
        ]
        
        article_cards = []
        
        for selector in possible_selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Найдены карточки по селектору: {selector}")
                article_cards.extend(cards)
                break
        
        # Если не нашли по специфичным селекторам, ищем по структуре
        if not article_cards:
            print("Карточки не найдены по стандартным селекторам, ищем по структуре...")
            # Ищем элементы, которые могут быть карточками статей
            # Обычно это div с ссылками и заголовками внутри
            potential_cards = soup.find_all('div', class_=True)
            article_cards = [card for card in potential_cards if 
                           card.find('a') and card.get_text(strip=True)]
        
        print(f"Найдено карточек: {len(article_cards)}")
        return article_cards
    
    def extract_article_info(self, card):
        """
        Извлекает информацию из одной карточки статьи
        
        Args:
            card (BeautifulSoup element): Элемент карточки статьи
            
        Returns:
            dict: Словарь с информацией о статье или None при ошибке
        """
        try:
            # Ищем заголовок статьи
            title_element = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or card.find('a')
            if not title_element:
                # Если не нашли заголовочный тег, берем первый ссылочный элемент
                title_element = card.find('a')
            
            if not title_element:
                return None
            
            # Извлекаем текст заголовка
            title = title_element.get_text(strip=True)
            if not title:
                return None
            
            # Ищем ссылку
            link_element = card.find('a')
            if not link_element or not link_element.get('href'):
                return None
            
            # Обрабатываем относительные ссылки
            link = link_element['href']
            if link.startswith('/'):
                link = urljoin(self.base_url, link)
            elif not link.startswith(('http://', 'https://')):
                link = urljoin(self.base_url, '/' + link)
            
            # Создаем словарь с информацией о статье
            article_info = {
                'title': title,
                'link': link
            }
            
            return article_info
            
        except Exception as e:
            print(f"Ошибка при обработке карточки: {e}")
            return None
    
    def parse_articles(self, url=None):
        """
        Основной метод парсинга статей
        
        Args:
            url (str): URL для парсинга (если None, используется базовый URL)
            
        Returns:
            list: Список словарей с информацией о статьях
        """
        if url is None:
            url = self.base_url
        
        # Получаем содержимое страницы
        soup = self.get_page_content(url)
        if not soup:
            return []
        
        # Находим карточки статей
        cards = self.find_article_cards(soup)
        
        # Извлекаем информацию из каждой карточки
        articles = []
        for i, card in enumerate(cards, 1):
            print(f"Обрабатываем карточку {i}/{len(cards)}...")
            article_info = self.extract_article_info(card)
            if article_info:
                articles.append(article_info)
                print(f"Извлечено: {article_info['title'][:50]}...")
        
        print(f"Парсинг завершен! Обработано статей: {len(articles)}")
        return articles
    
    def save_to_json(self, articles, filename="articles.json"):
        """
        Сохраняет результаты в JSON файл
        
        Args:
            articles (list): Список статей для сохранения
            filename (str): Имя файла для сохранения
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"Результаты сохранены в файл: {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")
    
    def display_results(self, articles):
        """
        Выводит результаты в консоль
        
        Args:
            articles (list): Список статей для отображения
        """
        print("\n" + "="*80)
        print("РЕЗУЛЬТАТЫ ПАРСИНГА:")
        print("="*80)
        
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Ссылка: {article['link']}")


def main():
    """
    Основная функция для запуска парсера
    """
    print("ЗАПУСК ПАРСЕРА СТАТЕЙ PEDSOVET.ORG")
    print("="*50)
    
    # Создаем экземпляр парсера
    parser = PedagogyParser()
    
    # Выполняем парсинг
    articles = parser.parse_articles()
    
    if articles:
        # Выводим результаты в консоль
        parser.display_results(articles)
        
        # Сохраняем в JSON
        parser.save_to_json(articles, "parsed_articles.json")
        
        print(f"Успешно обработано {len(articles)} статей!")
    else:
        print("Не удалось найти статьи. Возможно, изменилась структура сайта.")


# Точка входа в программу
if __name__ == "__main__":
    main()