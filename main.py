# Спарсить сайт Интерпола, вытащить как можно больше информации.
#Использовать классы, ответ дать в JSON-формате
#https://www.interpol.int/How-we-work/Notices/View-Red-Notices
#https://www.interpol.int/How-we-work/Notices/View-Yellow-Notices
import requests
import time
from bs4 import BeautifulSoup as BS
import json


class ParseRedList:
    def __init__(self, file_name):
#Без фильтра база Интерпола не выдает более 160 записей. Чтоб получить все записи, нужно пройти их различными фильтрами.
#Для фильтрации по странами происхождения и розыска создал список.
#Чтоб не искать то, чего нет, в список включил только те страны, которые разыскивают преступников.
        countries = [
            'AL', 'ZW', 'ZM', 'VN', 'VE', 'UZ', 'UY', 'US', '922', 'UA', 'TR', 'TH', 'TZ',
            'CH', 'SE', 'SR', 'LK', 'ES', 'ZA', 'SI', 'SK', 'SG', 'RW', 'RO', 'PL',
            'PH', 'PY', 'PG', 'PA', 'PK', 'NO', 'NG', 'NI', 'NL', 'NA', 'MM', 'MN', 'MD',
            'MX', 'MV', 'MY', 'MW', 'LU', 'LT', 'LV', 'KG', 'KE', 'KZ', 'JP', 'JM', 'IT',
            'IQ', 'IR', 'ID', 'IN', '914', 'HU', 'HK', 'GW', 'GT', 'GR', 'GH', 'DE', 'GE',
            'FR', 'FI', 'FJ', 'SZ', 'EE', 'GQ', 'EC', 'SV', 'DO', 'DK', 'CZ', 'CY', 'HR',
            'CR', 'CO', 'CN', 'CA', 'BG', 'BR', 'BW', 'BA', 'BO', 'BZ', 'BE', 'BD', 'BS',
            'AZ', 'AT', 'AU', 'AM', 'AR', 'AO',
            ]
        result_list = []
        for country in countries:
            counter = 0
            for age in range(17, 92):
#попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                try:
                    url = requests.get('https://ws-public.interpol.int/notices/v1/red?&ageMin=' + str(age) + '&ageMax=' + str(age) +'&arrestWarrantCountryId=' + country + '&resultPerPage=60')
                except:
                    time.sleep(300)
                    print('Страница не открывается. Подождем.')
                    url = requests.get('https://ws-public.interpol.int/notices/v1/red?&ageMin=' + str(age) + '&ageMax=' + str(age) +'&arrestWarrantCountryId=' + country + '&resultPerPage=60')
                soup = BS(url.text, 'html.parser')
                wanted_json = json.loads(str(soup))
                if wanted_json['total'] > 0:
                    wanted_list = wanted_json['_embedded']['notices']
                    for items in wanted_list:
                        wanted_href = items['_links']['self']['href']
                        print('Gotcha! ', items['forename'], items['name'])
#Мы получили ссылку на профиль разыскиваемого человека.
#попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                        try:
                            r = requests.get(wanted_href)
                        except:
                            time.sleep(300)
                            r = requests.get(wanted_href)
                        soup1 = BS(r.text, 'html.parser')
#AJAX выдает ответ в виде JSON, разберем его.
#Здесь мы попадаем в ловушку. Ответы 'Red' и 'Yellow' это JSON с разными полями.
#Если сохранить в результаты ответ от сервера "как есть", то можно при парсинге 'Yellow' просто унаследоваться и не переписывать функцию парсинга.
#Здесь я разберу ответ сервера, не стану передавать в результаты несколько ненужных полей.
                        profile_json = json.loads(str(soup1))
                        result_list.append({
                            'name': profile_json['name'],
                            'forename': profile_json['forename'],
                            'charge': profile_json['arrest_warrants'][0]['charge'],
                            'issuing_country_id': profile_json['arrest_warrants'][0]['issuing_country_id'],
                            'charge_translation': profile_json['arrest_warrants'][0]['charge_translation'],
                            'weight': profile_json['weight'],
                            'date_of_birth': profile_json['date_of_birth'],
                            'languages_spoken_ids': profile_json['languages_spoken_ids'],
                            'nationalities': profile_json['nationalities'],
                            'height': profile_json['height'],
                            'sex_id': profile_json['sex_id'],
                            'country_of_birth_id': profile_json['country_of_birth_id'],
                            'distinguishing_marks': profile_json['distinguishing_marks'],
                            'eyes_colors_id': profile_json['eyes_colors_id'],
                            'hairs_id': profile_json['hairs_id'],
                            'place_of_birth': profile_json['place_of_birth'],
                            'images_link': profile_json['_links']['images']['href'],
                                })
                else:
                    print(country, age, 'No criminals')
            #небольшая задержка, чтоб притвориться человеком
                counter += 1
                if counter % 10 == 0:
                    time.sleep(60)
        #Не жадничаем. Прошли страну, записали данные в файл. Если скрипт вылетит, то всегда можно продолжить.
            print('Данные из страны получены. Записываем данные в файл.')
            results_json = json.dumps(result_list)
            with open(file_name, 'a') as file:
                file.write(results_json)
            result_list = []
        # прошли страну, задержались, чтоб притвориться человеком.
            time.sleep(300)


#В базе Интерпола более 3000 преступников, объявленных в розыск Россией.
#При лимите выдачи в 160, надо использовать фильтры по возрасту, полу и пагинацию.
#Иначе результаты будут неполными.
class ParseRussiaRedNotes:

    def __init__(self, file_name, age_min, age_max):
        sex_id = ['M', 'F']
        result_list = []
        counter = 0
        for age in range(age_min, age_max):
            for sex in sex_id:
                for page in range (1, 4):
                    try:
                        url = requests.get(
                        'https://ws-public.interpol.int/notices/v1/red?ageMin='+ str(age) + '&ageMax=' + str(age) + '&sexId=' + sex +'&arrestWarrantCountryId=RU&resultPerPage=70&page='+ str(page))

                    except:
                        time.sleep(300)
                        url = requests.get(
                        'https://ws-public.interpol.int/notices/v1/red?ageMin='+ str(age) + '&ageMax=' + str(age) + '&sexId=' + sex +'&arrestWarrantCountryId=RU&resultPerPage=70&page=' +str(page))
                    soup = BS(url.text, 'html.parser')
                    wanted_json = json.loads(str(soup))
                    if wanted_json['total'] > 0:
                        wanted_list = wanted_json['_embedded']['notices']
                        for items in wanted_list:
                            wanted_href = items['_links']['self']['href']
                            print('Gotcha! ', items['forename'], items['name'])
#получили ссылку на профиль разыскиваемого человека.
                    # попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                            try:
                                r = requests.get(wanted_href)
                            except:
                                time.sleep(300)
                                r = requests.get(wanted_href)
                            soup1 = BS(r.text, 'html.parser')
#AJAX выдает ответ в виде JSON, разберем его.
                            profile_json = json.loads(str(soup1))
                            result_list.append({
                            'name': profile_json['name'],
                            'forename': profile_json['forename'],
                            'charge': profile_json['arrest_warrants'][0]['charge'],
                            'issuing_country_id': profile_json['arrest_warrants'][0]['issuing_country_id'],
                            'charge_translation': profile_json['arrest_warrants'][0]['charge_translation'],
                            'weight': profile_json['weight'],
                            'date_of_birth': profile_json['date_of_birth'],
                            'languages_spoken_ids': profile_json['languages_spoken_ids'],
                            'nationalities': profile_json['nationalities'],
                            'height': profile_json['height'],
                            'sex_id': profile_json['sex_id'],
                            'country_of_birth_id': profile_json['country_of_birth_id'],
                            'distinguishing_marks': profile_json['distinguishing_marks'],
                            'eyes_colors_id': profile_json['eyes_colors_id'],
                            'hairs_id': profile_json['hairs_id'],
                            'place_of_birth': profile_json['place_of_birth'],
                            'images_link': profile_json['_links']['images']['href'],
                                })
                    else:
                        print(age, 'No criminals')
#небольшая задержка, чтоб притвориться человеком
                    counter += 1
                    if counter % 10 == 0:
                        time.sleep(60)
#Не жадничаем. Прошли год возраста, записали данные в файл. Если скрипт вылетит, то всегда можно продолжить.
            print('Данные из страны получены. Записываем данные в файл.')
            results_json = json.dumps(result_list)
            with open(file_name, 'a') as file:
                file.write(results_json)
            result_list = []
#прошли год возраста, задержались, чтоб притвориться человеком.
            time.sleep(300)


#парсим Желтый список Интерпола(пропавших людей).
class ParseYellowNotes:

    def __init__(self, file_name):
#cписок стран для жертв отличается от списка стран для преступников
        countries = [
            'AE', 'AF', 'AG', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AZ', 'BA', 'BD', 'BG', 'BH', 'BJ', 'BO',
            'BR', 'BS', 'BT', 'BT', 'BW', 'BY', 'BE', 'BZ', 'CA', 'CD', 'CG', 'CH', 'CI', 'CL', 'CM', 'CN',
            'CO', 'CR', 'CU', 'CV', 'CY', 'CZ', 'DE', 'DJ', 'DK', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ER', 'ES',
            'ET', 'FI', 'FJ', 'FR', 'GE', 'GF', 'GH', 'GN', 'GR', 'GT', 'HN', 'HR', 'HT', 'HU', 'ID', 'IE',
            'IL', 'IN', 'IQ', 'IR', 'IS', 'IT', 'JM', 'JO', 'JP', 'KG', 'KH', 'KR', 'KW', 'KZ', 'LA', 'LB',
            'LK', 'LR', 'LT', 'LU', 'LV', 'LY', 'MA', 'MD', 'ME', 'MG', 'MK', 'ML', 'MM', 'MN', 'MT', 'MV',
            'MW', 'MX', 'MY', 'MZ', 'NA', 'NG', 'NI', 'NL', 'NO', 'NP', 'OM', 'PA', 'PE', 'PH', 'PK', 'PL',
            'PS', 'PT', 'PY', 'RO', 'RS', 'RU', 'RW', 'SA', 'SC', 'SD', 'SE', 'SG', 'SI', 'SK', 'SN', 'SO',
            'SR', 'SV', 'SY', 'SZ', 'TH', 'TJ', 'TL', 'TN', 'TR', 'TT', 'TZ', 'UA', 'UG', 'UK', 'US', 'UY',
            'UZ', 'VE', 'VN', 'YE', 'ZA', 'ZM', 'ZW'
        ]
        result_list = []
        for country in countries:
            counter = 0
#возраст преступников и жертв отличается. Преступники не бывают младше 17, в желтый список попадают даже новорожденные дети.
            for age in range(0, 92):
#попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                try:
                    url = requests.get('https://ws-public.interpol.int/notices/v1/yellow?&nationality='+ country + '&ageMin=' +str(age) +'&ageMax=' +str(age)+'&resultPerPage=65')
                except:
                    print('Страница не открывается. Подождем.')
                    time.sleep(360)
                    url = requests.get('https://ws-public.interpol.int/notices/v1/yellow?&nationality='+ country + '&ageMin=' +str(age) +'&ageMax=' +str(age)+'&resultPerPage=65')
                soup = BS(url.text, 'html.parser')
                wanted_json = json.loads(str(soup))
                if wanted_json['total'] > 0:
                    wanted_list = wanted_json['_embedded']['notices']
                    for items in wanted_list:
                        wanted_href = items['_links']['self']['href']
                        print('Missed! ', items['forename'], items['name'])
#Мы получили ссылку на профиль разыскиваемого человека.
#попытку получить данные оборачиваем в try-except, чтоб при срабатывании защиты, не выбило скрипт.
                        try:
                            r = requests.get(wanted_href)
                        except:
                            time.sleep(300)
                            r = requests.get(wanted_href)
                        soup1 = BS(r.text, 'html.parser')
#AJAX выдает ответ в виде JSON, разберем его.
#Для преступников и жертв разные таблицы, в частности в список жертв попадают дети, и полями будут имена родителей.
                        profile_json = json.loads(str(soup1))
                        result_list.append({
                            'birth_name': profile_json['birth_name'],
                            'name': profile_json['name'],
                            'forename': profile_json['forename'],
                            'father_name': profile_json['father_name'],
                            'father_forename': profile_json['father_forename'],
                            'mother_name': profile_json['mother_forename'],
                            'mother_forename': profile_json['mother_forename'],
                            'weight': profile_json['weight'],
                            'date_of_birth': profile_json['date_of_birth'],
                            'languages_spoken_ids': profile_json['languages_spoken_ids'],
                            'nationalities': profile_json['nationalities'],
                            'height': profile_json['height'],
                            'sex_id': profile_json['sex_id'],
                            'country': profile_json['country'],
                            'country_of_birth_id': profile_json['country_of_birth_id'],
                            'date_of_event': profile_json['date_of_event'],
                            'distinguishing_marks': profile_json['distinguishing_marks'],
                            'eyes_colors_id': profile_json['eyes_colors_id'],
                            'hairs_id': profile_json['hairs_id'],
                            'place_of_birth': profile_json['place_of_birth'],
                            'images_link': profile_json['_links']['images']['href'],
                                })
                else:
                    print(country, age, 'No missed persons')
#небольшая задержка, чтоб притвориться человеком
                counter += 1
                if counter % 20 == 0:
                    time.sleep(60)
#Не жадничаем. Прошли страну, записали данные в файл. Если скрипт вылетит, то всегда можно продолжить.
            print('Данные из страны получены. Записываем данные в файл.')
            results_json = json.dumps(result_list)
            with open(file_name, 'a') as file:
                file.write(results_json)
            result_list = []
#прошли страну, задержались, чтоб притвориться человеком.
            time.sleep(300)



if __name__ == '__main__':
    ParseYellowNotes('results/yellow-list.json')


