from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os


class SeleniumPedagogyParser:
    """
    Парсер для pedsovet.org с использованием Selenium
    для работы с JavaScript-контентом
    """
    
    def __init__(self):
        self.base_url = "https://pedsovet.org"
        self.setup_driver()
    
    def setup_driver(self):
        """Настраивает Chrome driver"""
        print("Настраиваем браузер...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Фоновый режим
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Используем webdriver-manager для автоматической загрузки драйвера
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def get_page_content(self):
        """Получает содержимое страницы с ожиданием загрузки"""
        print(f"Загружаем страницу {self.base_url}...")
        self.driver.get(self.base_url)
        
        # Ждем загрузки страницы
        time.sleep(3)
        
        # Прокручиваем страницу чтобы подгрузился контент
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Получаем HTML после выполнения JavaScript
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        print("Страница загружена")
        return soup
    
    def find_articles(self, soup):
        """Ищет статьи на странице"""
        print("Ищем статьи...")
        
        articles = []
        
        # Пробуем разные селекторы для статей
        selectors = [
            'article',
            '[class*="article"]',
            '[class*="news"]',
            '[class*="post"]',
            '[class*="content"]',
            '.card',
            '.item',
            '.material'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 5:  # Если найдено достаточно элементов
                print(f"Найдены элементы по селектору: {selector} - {len(elements)} шт.")
                articles.extend(elements)
        
        # Если не нашли по селекторам, ищем по структуре
        if not articles:
            print("Ищем статьи по структуре...")
            # Ищем все элементы с ссылками и значительным текстом
            all_elements = soup.find_all(['div', 'section', 'article'])
            articles = [elem for elem in all_elements 
                       if elem.find('a') and len(elem.get_text(strip=True)) > 50]
        
        print(f"Всего найдено кандидатов в статьи: {len(articles)}")
        return articles
    
    def extract_article_info(self, article_element):
        """Извлекает информацию из элемента статьи"""
        try:
            # Ищем заголовок
            title = None
            link = None
            
            # Ищем в заголовочных тегах
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                header = article_element.find(tag)
                if header and header.get_text(strip=True):
                    title = header.get_text(strip=True)
                    break
            
            # Если не нашли заголовок, ищем текст ссылки
            if not title:
                link_elem = article_element.find('a')
                if link_elem:
                    title = link_elem.get_text(strip=True)
            
            # Ищем ссылку
            link_elem = article_element.find('a')
            if link_elem and link_elem.get('href'):
                link = link_elem.get('href')
                # Делаем ссылку абсолютной
                if link.startswith('/'):
                    link = self.base_url + link
                elif not link.startswith(('http://', 'https://')):
                    link = self.base_url + '/' + link
            
            # Проверяем что есть и заголовок и ссылка
            if title and link and len(title) > 10:
                return {
                    'title': title,
                    'link': link
                }
            
            return None
            
        except Exception as e:
            print(f"Ошибка при извлечении: {e}")
            return None
    
    def parse(self):
        """Основной метод парсинга"""
        print("ЗАПУСК ПАРСЕРА PEDSOVET.ORG (SELENIUM)")
        print("=" * 50)
        
        try:
            # Получаем контент
            soup = self.get_page_content()
            
            # Ищем статьи
            article_elements = self.find_articles(soup)
            
            # Извлекаем информацию
            articles = []
            for i, element in enumerate(article_elements, 1):
                print(f"Обрабатываем элемент {i}/{len(article_elements)}...")
                article_info = self.extract_article_info(element)
                if article_info:
                    articles.append(article_info)
                    print(f"  Найдена статья: {article_info['title'][:50]}...")
            
            # Выводим результаты
            self.display_results(articles)
            
            # Сохраняем
            if articles:
                self.save_to_json(articles)
            
            return articles
            
        except Exception as e:
            print(f"Ошибка при парсинге: {e}")
            return []
        
        finally:
            # Закрываем браузер
            self.driver.quit()
    
    def display_results(self, articles):
        """Выводит результаты"""
        print("\n" + "=" * 80)
        print("РЕЗУЛЬТАТЫ ПАРСИНГА:")
        print("=" * 80)
        
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Ссылка: {article['link']}")
            print()
    
    def save_to_json(self, articles, filename="selenium_articles.json"):
        """Сохраняет в JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"Результаты сохранены в {filename}")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")


def main():
    parser = SeleniumPedagogyParser()
    articles = parser.parse()
    
    if articles:
        print(f"Успешно найдено статей: {len(articles)}")
    else:
        print("Статьи не найдены")


if __name__ == "__main__":
    main()
