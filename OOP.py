#Здесь напишем код для парсинга базы Интерпола в более объектном стиле
import requests
import time
from bs4 import BeautifulSoup as BS
import json


class ParseRedOrYellowNotices:
#url1, url2, url3, url4 - "куски" ссылки для парсинга
#countries - список стран, которые будем парсить.
#поскольку в этом классе результаты сохраняются только по окончанию отработки всего алгоритма, рекомендуется тянуть маленькими порциями

    def __init__(self, countries, url1, url2, url3, url4):
        result_list = []
        for country in countries:
            counter = 0
            for age in range(17, 92):
#попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                try:
                    url = requests.get(url1 + str(age) + url2 + str(age) +url3 + country + url4)
                except:
                    time.sleep(300)
                    url = requests.get('https://ws-public.interpol.int/notices/v1/red?&ageMin=' + str(age) + '&ageMax=' + str(age) +'&arrestWarrantCountryId=' + country + '&resultPerPage=60')
                soup = BS(url.text, 'html.parser')
                wanted_json = json.loads(str(soup))
                if wanted_json['total'] > 0:
                    wanted_list = wanted_json['_embedded']['notices']
                    for items in wanted_list:
                        wanted_href = items['_links']['self']['href']
                        print(items['forename'], items['name'])
#Мы получили ссылку на профиль разыскиваемого человека.
#попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                        try:
                            r = requests.get(wanted_href)
                        except:
                            time.sleep(300)
                            r = requests.get(wanted_href)
                        soup1 = BS(r.text, 'html.parser')
#AJAX выдает ответ в виде JSON.
#Преобразуем его в словарь с помощью встроенного модуля.
#В прошлой версии я разбирал словари, убирал ненужные строки, как то "перевод обвинения", которая везде пустая, итд.
#Здесь все намного проще.
                        profile_json = json.loads(str(soup1))
                        result_list.append(profile_json)
                else:
                    print(country, age, 'No criminals')
            #небольшая задержка, чтоб притвориться человеком
                counter += 1
                if counter % 10 == 0:
                    time.sleep(60)
            print('Данные из страны получены. Записываем данные в файл.')
#прошли страну, задержались, чтоб притвориться человеком.
            time.sleep(300)

        self.result_list = result_list

#определим метод сохранения результата в json-формат
    def to_json(self, file_name):
        results_json = json.dumps(self.result_list)
        with open(file_name, 'a') as file:
            file.write(results_json)

#Cпарсим красный список из России.
#Из-за количества записей, фильтрами будут выступать возраст, пол и пагинация.
class ParseRussiaRedNotices(ParseRedOrYellowNotices):

#метод сохранения файлов в json-формат унаследуем, конструктор класса переопределим
    def __init__(self, age_min, age_max):
        sex_id = ['M', 'F']
        result_list = []
        counter = 0
        for age in range(age_min, age_max):
            for sex in sex_id:
                for page in range(1, 4):
                    try:
                        url = requests.get(
                            'https://ws-public.interpol.int/notices/v1/red?ageMin=' + str(age) + '&ageMax=' + str(
                                age) + '&sexId=' + sex + '&arrestWarrantCountryId=RU&resultPerPage=70&page=' + str(page))

                    except:
                        time.sleep(300)
                        url = requests.get(
                            'https://ws-public.interpol.int/notices/v1/red?ageMin=' + str(age) + '&ageMax=' + str(
                                age) + '&sexId=' + sex + '&arrestWarrantCountryId=RU&resultPerPage=70&page=' + str(page))
                    soup = BS(url.text, 'html.parser')
                    wanted_json = json.loads(str(soup))
                    if wanted_json['total'] > 0:
                        wanted_list = wanted_json['_embedded']['notices']
                        for items in wanted_list:
                            wanted_href = items['_links']['self']['href']
                            print('Gotcha! ', items['forename'], items['name'])
                        # получили ссылку на профиль разыскиваемого человека.
                        # попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                            try:
                                r = requests.get(wanted_href)
                            except:
                                time.sleep(300)
                                r = requests.get(wanted_href)
                            soup1 = BS(r.text, 'html.parser')
#AJAX выдает ответ в виде JSON, переводим его в словарь и добавляем в список результатов.
                            profile_json = json.loads(str(soup1))
                            result_list.append(profile_json)
                else:
                    print(age, 'No criminals')
#небольшая задержка, чтоб притвориться человеком
                counter += 1
                if counter % 10 == 0:
                    time.sleep(60)
#прошли группу людей одного возраста, задержались, притворились человеком.
            time.sleep(300)
#наш список результатов теперь это аттрибут класса.
#унаследованным методом 'to_json' можем сохранить его в файл
        self.result_list = result_list





