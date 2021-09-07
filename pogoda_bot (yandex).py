import sqlite3, requests, telebot
from time import sleep, time, strftime, localtime
bot = telebot.TeleBot(token)

def case(text):
    r = requests.get('https://ws3.morpher.ru/russian/declension', params={'s':text, 
     'format':'json',  'flags':'Inanimate',  'token':'0b541c78-c09e-4153-82b8-9b24772e0188'})
    if r.status_code == 200:
        r = r.json()['П']
    else:
        r = requests.get('http://htmlweb.ru/json/service/inflect', params={'inflect':text,  'grammems':'пр'})
        if 'error' not in r.json():
            r = r.json()['items'][0]
        else:
            return False
    return 'В ' + r.title()


def write(name, nik, q, f, time):
    if len(q) > 30:
        q = q[:31] + '...'
    with open('stat.txt', 'a', encoding='utf-8') as (file):
        file.write(name + '  @' + nik + '  ' + q + '  ' + f + '  ' + strftime('%H:%M:%S %m.%d.%Y', localtime()) + '  ' + str(round(time, 3)) + '\n\n')


def speller(text):
    r = requests.get('https://speller.yandex.net/services/spellservice.json/checkText', params={'text': text})
    r = r.json()
    if r == []:
        c = case(text)
        if c != False:
            return c
    return False


@bot.message_handler(commands=['start', 'help'])
def help(m):
    id_w = m.chat.id
    bot.send_message(id_w, '\nДобро пожаловать в ПогодаБот!!!\n\n\nДля того чтобы узнать погоду в каком-то городе отправьте Боту название этого города.\n\nЕсли Бот получит название города, которого не существует, он выведет об этом сообщение и Вам придётся набрать название города заново.\n\nЧтобы заново прочесть это сообщение, наберите команду /start или /help.\n\n\nПриятной погоды!!!')


@bot.message_handler(content_types=['text'])
def print_weather(m):
    t = time()
    id_w = m.chat.id
    sp = speller(m.text)
    if sp != False:
        k = requests.get('https://geocode-maps.yandex.ru/1.x', params={'geocode':m.text, 
         'apikey':'7027fa5c-d6b0-4f51-8671-9060ab1ffa0c',  'format':'json'})
        if k.json()['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found'] == '0':
            bot.send_message(id_w, 'Программа такого места не нашла')
            write(m.from_user.first_name, m.from_user.username, m.text, 'False', time() - t)
            return 0
        k = k.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
        r = requests.get('https://api.weather.yandex.ru/v2/informers', params={'lon':k[0], 
         'lat':k[1], 
         'lang':'ru_RU'},
          headers={'X-Yandex-API-Key': '3dad6803-513f-47fc-b852-58f47c3495ce'})
        r = r.json()
        bot.send_message(id_w, sp + ' сейчас ' + str(r['fact']['temp']) + '°C')
        write(m.from_user.first_name, m.from_user.username, m.text, 'True', time() - t)
    else:
        bot.send_message(id_w, 'Программа такого места не нашла')
        write(m.from_user.first_name, m.from_user.username, m.text, 'False', time() - t)


while True:
    try:
        bot.polling(none_stop=True)
    except:
        sleep(1)
