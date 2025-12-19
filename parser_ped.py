import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin


class PedagogyParser:
    """
    Парсер для сайта pedsovet.org с использованием BeautifulSoup
    """
    
    def __init__(self):
        self.base_url = "https://pedsovet.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_page(self):
        """Получаем HTML страницу"""
        print(f"Загружаем главную страницу: {self.base_url}")
        
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()  # Проверяем на ошибки
            
            # Создаем объект BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            print("✓ Страница успешно загружена")
            return soup
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Ошибка при загрузке: {e}")
            return None
    
    def find_all_elements_demo(self, soup):
        """Демонстрация всех методов из задания"""
        print("\n" + "="*60)
        print("ДЕМОНСТРАЦИЯ МЕТОДОВ BEAUTIFULSOUP:")
        print("="*60)
        
        # 1. Поиск по тегу
        print("\n1. Поиск по тегу <a> (все ссылки):")
        all_links = soup.find_all('a')
        print(f"   Найдено ссылок: {len(all_links)}")
        if all_links[:3]:  # Покажем первые 3
            for i, link in enumerate(all_links[:3], 1):
                text = link.text.strip()[:50] + "..." if len(link.text.strip()) > 50 else link.text.strip()
                print(f"   {i}. Текст: {text}")
        
        # 2. Поиск по классу
        print("\n2. Поиск по классу 'article':")
        articles_by_class = soup.find_all(class_='article')
        print(f"   Найдено элементов: {len(articles_by_class)}")
        
        # 3. Поиск по id
        print("\n3. Поиск по id (любому):")
        # Ищем любой элемент с id
        element_with_id = soup.find(id=True)
        if element_with_id:
            id_name = list(element_with_id.attrs.get('id', []))[0] if isinstance(element_with_id.attrs.get('id', []), list) else element_with_id.attrs.get('id', '')
            print(f"   Найден элемент с id='{id_name}'")
        else:
            print("   Элементы с id не найдены")
        
        # 4. Поиск по атрибуту
        print("\n4. Поиск по атрибуту 'href' (ссылки):")
        links_with_href = soup.find_all(href=True)
        print(f"   Найдено ссылок с атрибутом href: {len(links_with_href)}")
        
        # 5. CSS селекторы
        print("\n5. Поиск с помощью CSS селекторов:")
        # Все заголовки
        headers = soup.select('h1, h2, h3, h4')
        print(f"   Найдено заголовков (h1-h4): {len(headers)}")
        
        return True
    
    def parse_articles(self, soup):
        """Основной парсинг статей"""
        print("\n" + "="*60)
        print("ПАРСИНГ СТАТЕЙ:")
        print("="*60)
        
        articles = []
        
        # СПОСОБ 1: Ищем статьи по структуре (все элементы с значительным текстом и ссылкой)
        print("Способ 1: Поиск по структуре (div, article, section с ссылками)")
        
        # Ищем в разных типах контейнеров
        containers = soup.find_all(['div', 'article', 'section'])
        
        for container in containers:
            # Ищем ссылку внутри контейнера
            link_tag = container.find('a')
            
            if link_tag and link_tag.get('href'):
                # Ищем заголовок (h1-h4) или используем текст ссылки
                title_tag = container.find(['h1', 'h2', 'h3', 'h4'])
                
                if title_tag:
                    title = title_tag.text.strip()
                else:
                    title = link_tag.text.strip()
                
                # Получаем ссылку
                link = link_tag.get('href')
                
                # Делаем ссылку абсолютной
                if link:
                    link = urljoin(self.base_url, link)
                
                # Проверяем, что это похоже на статью (есть заголовок и ссылка)
                if title and len(title) > 10 and link:
                    article_data = {
                        'title': title,
                        'link': link
                    }
                    
                    # Добавляем только уникальные статьи
                    if article_data not in articles:
                        articles.append(article_data)
        
        # СПОСОБ 2: Альтернативный поиск (по карточкам)
        print("\nСпособ 2: Поиск по карточкам (элементы с классами card, item, post)")
        
        card_classes = ['card', 'item', 'post', 'news', 'article', 'material']
        
        for card_class in card_classes:
            cards = soup.find_all(class_=card_class)
            
            for card in cards:
                link_tag = card.find('a')
                if link_tag and link_tag.get('href'):
                    title = link_tag.text.strip()
                    if not title or len(title) < 10:
                        # Ищем заголовок в других тегах
                        header = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        if header:
                            title = header.text.strip()
                    
                    link = urljoin(self.base_url, link_tag.get('href'))
                    
                    if title and len(title) > 10 and link:
                        article_data = {
                            'title': title,
                            'link': link
                        }
                        
                        # Проверяем на дубликаты по заголовку и ссылке
                        is_duplicate = False
                        for existing_article in articles:
                            if (existing_article['title'] == title or 
                                existing_article['link'] == link):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            articles.append(article_data)
        
        # Ограничим количество статей для наглядности
        articles = articles[:15]
        
        print(f"\nНайдено статей: {len(articles)}")
        return articles
    
    def display_results(self, articles):
        """Выводим результаты"""
        print("\n" + "="*80)
        print("НАЙДЕННЫЕ СТАТЬИ:")
        print("="*80)
        
        for i, article in enumerate(articles, 1):
            print(f"{i:2}. {article['title'][:70]}{'...' if len(article['title']) > 70 else ''}")
            print(f"    Ссылка: {article['link']}")
            print()
    
    def save_to_json(self, articles, filename="articles.json"):
        """Сохраняем в JSON файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"\n✓ Результаты сохранены в файл: {filename}")
            return True
        except Exception as e:
            print(f"\n✗ Ошибка при сохранении: {e}")
            return False
    
    def run(self):
        """Запуск парсера"""
        print("="*60)
        print("ПАРСЕР ДЛЯ PEDSOVET.ORG (BeautifulSoup)")
        print("="*60)
        
        # 1. Получаем страницу
        soup = self.get_page()
        if not soup:
            return []
        
        # 2. Демонстрация методов из задания
        self.find_all_elements_demo(soup)
        
        # 3. Парсим статьи
        articles = self.parse_articles(soup)
        
        # 4. Показываем результаты
        if articles:
            self.display_results(articles)
            
            # 5. Сохраняем
            self.save_to_json(articles)
            
            print(f"\n{'='*60}")
            print(f"ПАРСИНГ ЗАВЕРШЕН! Найдено статей: {len(articles)}")
            print(f"{'='*60}")
        else:
            print("\n✗ Статьи не найдены. Попробуйте другие селекторы.")
        
        return articles


def main():
    """Главная функция"""
    parser = PedagogyParser()
    articles = parser.run()
    
    # Краткая статистика
    if articles:
        print(f"\n📊 Статистика:")
        print(f"   • Всего статей: {len(articles)}")
        print(f"   • Пример заголовка: {articles[0]['title'][:50]}...")
        print(f"   • Пример ссылки: {articles[0]['link'][:60]}...")


if __name__ == "__main__":
    main()