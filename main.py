import requests
import bs4
import time
from selenium import webdriver
import json


def json_chars(string):
    """ Excludes json control characters in string """
    return string.replace('"', '\'').replace('\t', '  ')


print("Введите ключевое слово")
word = input()
url = 'https://play.google.com/store/search?q='+word+'&c=apps'
driv = webdriver.Firefox(executable_path=r"geckodriver.exe")
driv.get(url)
last_height = driv.execute_script("return document.body.scrollHeight")
while driv.find_element_by_id('show-more-button').get_attribute('style') != '':
    driv.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driv.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
button = driv.find_element_by_id('show-more-button')
if button.get_attribute('style') == '':
    button.click()
main_page = bs4.BeautifulSoup(driv.page_source, 'html.parser')
title = main_page.select('.details .title')
driv.close()
full_str = r'['
for i in range(0, len(title)):
    if word.lower() in title[i].getText().lower():
        name = json_chars(title[i].getText()[2:-2])
        r = requests.get('https://play.google.com' + title[i].get('href'))
        description_page = bs4.BeautifulSoup(r.text, "html.parser")
        description = description_page.select('.show-more-content')[0]
        if word.lower() in description_page.getText().lower():
            description = json_chars(description.getText())
            href = 'https://play.google.com'+title[i].get('href')
            author = description_page.select('.document-subtitle')[0].getText()
            auhtor = json_chars(author)
            category = description_page.select('.document-subtitle')[4]
            category = category.getText()
            last_update = description_page.select('.document-subtitle')[1]
            last_update = last_update.getText()[2:]
            if len(description_page.select('.score')) != 0:
                average_score = description_page.select('.score')[0].getText()
            else:
                average_score = 'значение отсутствует'
            if len(description_page.select('.reviews-num')) != 0:
                score = description_page.select('.reviews-num\
                ')[0].getText().replace('\xa0', '').replace(' ', '')
            else:
                score = 'значение отсутствует'
            full_str += "{\"Название\": \"" + name
            full_str += "\",\"url\":\"" + href
            full_str += "\",\"Автор\":\"" + author
            full_str += "\",\"Категория\":\"" + category
            full_str += "\",\"Описание\":\"" + description
            full_str += "\",\"Средняя оценка\":\"" + average_score
            full_str += "\",\"Количество оценок\":\"" + score
            full_str += "\",\"Последнее обновление\":\"" + last_update
            full_str += "\"},"
full_str = full_str[0:-1] + ']'
parsed_str = json.loads(full_str)
with open('data_'+word+'.txt', 'w') as outfile:
    json.dump(parsed_str, outfile)
print('Done')
