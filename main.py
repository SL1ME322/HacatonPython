import json
import codecs
import re
from bs4 import BeautifulSoup
import requests

def find_cite_web_links(text):
     pattern = r'\[\[Файл:.+?\]\]|\[\[.+?\]\]|\[\[Категория:.+?\]\]|<ref.+?cite web.+?</ref>'
      
     links = re.findall(pattern,text)
     return links

def find_category_names(text):
    category_pattern =  r'\[\[Категория:(.*?)\]\]'
    categories = re.findall(category_pattern, text)
    category_names = [category.split('|')[0].strip().replace(' ','_') for category in categories]
    return category_names

def extract_url_info(url):
    if "title=" in url:
        parts = url.split("|")
        title = parts[1].replace("title=","") if len(parts) > 1 else "-"
        fixedUrl = url.split("|", 1)[0]

        print(fixedUrl)
    else:
        title = "-"
        fixedUrl = url
        
    response = requests.get(fixedUrl)
    soup = BeautifulSoup(response.content, "html.parser")
    

    author_tag = soup.find("meta", property="article:author")
    if author_tag:
        author = author_tag["content"]
    else:
        author = "-"

    date_tag = soup.find("meta", property="article:published_time")
    if date_tag:
        date = date_tag["content"]
    else:
        date = "-"

    website_tag = soup.find("meta", property="og:site_name")
    if website_tag:
        website = website_tag["content"]
    else:
        website = "-"

    publisher_tag = soup.find("meta", property="article:publisher")
    if publisher_tag:
         publisher = publisher_tag["content"]
    else:
        publisher = "-"
    return title, author, date, website, publisher, fixedUrl

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8' ) as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print('Файл не найден')
        return None
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON.")
        return None

def decode_unicode(data):
    try:
        decoded_data = codecs.decode(data, 'unicode-escape')
        return decoded_data
    except UnicodeDecodeError:
        print("Ошибка декодирования")
        return None


def main():
    file_path = input("Путь к JSON\n")
    json_data = read_json_file(file_path)
    if json_data:
        print("Содержание файла JSON")
        json_string = json.dumps(json_data)
        decoded_data = decode_unicode(json_string)
        
        web_links = find_cite_web_links(decoded_data)
        url_count = 0
        for link in web_links:
            if "url=" in link:
                url_count += 1   
                url = re.search(r'url=(https?://\S+)', link).group(1)
                title, author, date, website, publisher, fixedUrl = extract_url_info(url)
                print(f"{url_count}. {title}")
                print(f"   Ссылка: {fixedUrl}")
                print(f"   Информация о ссылке: Автор - {author}, Дата - {date}, Веб-сайт - {website}, Издатель - {publisher}")
                
        categories = find_category_names(decoded_data)
        print("Найденные категории:")
        for category in categories:
            print("https://ru.wikipedia.org/wiki/Категория:" + category)
    else:
        print("Цитаты не найдены")    
if __name__ == "__main__":
    main()
 