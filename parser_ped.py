import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


class PedagogyParser:
    """
    Парсер карточек статей с сайта pedsovet.org
    """
    
    def __init__(self):
        self.base_url = "https://pedsovet.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page(self):
        """Загружаем HTML страницу"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке страницы: {e}")
            return None
    
    def parse_article_cards(self, soup):
        """
        Ищем карточки статей и извлекаем данные
        """
        articles = []
        
        # Основные селекторы для поиска карточек
        card_selectors = [
            '.card',
            '.article-card', 
            '.news-item',
            '.material-card',
            '[class*="card"]',
            '[class*="item"]',
        ]
        
        # Пробуем разные селекторы
        for selector in card_selectors:
            cards = soup.select(selector)
            if cards:
                for card in cards:
                    article_data = self.extract_article_data(card)
                    if article_data and article_data not in articles:
                        articles.append(article_data)
        
        # Дополнительный поиск по структуре
        if len(articles) < 5:
            containers = soup.find_all(['div', 'article', 'section'])
            for container in containers:
                if container.find('a') and len(container.get_text(strip=True)) > 30:
                    article_data = self.extract_article_data(container)
                    if article_data and article_data not in articles:
                        articles.append(article_data)
        
        return articles[:15]  # Ограничиваем для наглядности
    
    def extract_article_data(self, card):
        """Извлекаем данные из карточки"""
        try:
            # Ищем заголовок
            title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if title_elem:
                title = title_elem.get_text(strip=True)
            else:
                link_elem = card.find('a')
                title = link_elem.get_text(strip=True) if link_elem else ""
            
            # Ищем ссылку
            link_elem = card.find('a')
            if link_elem and link_elem.get('href'):
                link = urljoin(self.base_url, link_elem.get('href'))
            else:
                return None
            
            # Проверяем данные
            if title and len(title) > 5 and link:
                return {'title': title, 'link': link}
            
            return None
            
        except Exception:
            return None
    
    def run(self):
        """Основной метод запуска парсера"""
        print("="*60)
        print("ПАРСИНГ КАРТОЧЕК СТАТЕЙ С PEDSOVET.ORG")
        print("="*60)
        
        # Получаем страницу
        soup = self.get_page()
        if not soup:
            return []
        
        # Парсим карточки
        articles = self.parse_article_cards(soup)
        
        # Выводим результаты
        if articles:
            print(f"\nНайдено статей: {len(articles)}\n")
            
            for i, article in enumerate(articles, 1):
                title = article['title']
                if len(title) > 70:
                    title = title[:67] + "..."
                print(f"{i:2}. {title}")
                print(f"    {article['link']}\n")
            
            # Сохраняем в JSON
            try:
                with open('articles.json', 'w', encoding='utf-8') as f:
                    json.dump(articles, f, ensure_ascii=False, indent=2)
                print(f"✓ Результаты сохранены в файл: articles.json")
            except Exception as e:
                print(f"✗ Ошибка при сохранении: {e}")
        else:
            print("\nСтатьи не найдены")
        
        print("\n" + "="*60)
        return articles


def main():
    """Точка входа"""
    parser = PedagogyParser()
    articles = parser.run()


if __name__ == "__main__":
    main()
