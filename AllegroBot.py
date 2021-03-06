#  AllegroBot.py - A quick Bot that searches for the items you want to buy :-)
#  Adding a '-p' (lowercase) followed by a number filters items that cost less or the same.
#  Adding a '-P' (UPPERCASE) followed by a page number searches through P pages.

import os
import re
import sys
import logging
import requests
import send2trash
from bs4 import BeautifulSoup
from utils import value_strip, search_strip, convert_price_to_number

search_for = ''
item_list = []
if len(sys.argv) > 1:
    search_for = ' '.join(sys.argv[1:])

url = 'https://allegro.pl/listing?string=' + search_strip(search_for)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}

page = requests.get(url, headers=headers)
soup = BeautifulSoup(page.text, features='lxml')

price_to = value_strip('p', search_for)
page_to = value_strip('P', search_for)

item_container = soup.findAll('div', {'class': 'mpof_ki myre_zn _9c44d_1Hxbq'})
if page_to:
    for p_num in range(2, int(page_to)+1):
        url = 'https://allegro.pl/listing?string=' + search_strip(search_for) + f'&p={p_num}'
        item_container += item_container

path = os.path.join(os.getcwd(), 'AllegroBot')
if len(item_container) != 0:
    if not os.path.exists(path):
        print(f'Creating folder {os.path.basename(path)}...')
        os.mkdir(path)
    os.chdir(path)
else:
    print('No items match your search.')
    quit()

filename = f"allegro_{search_strip(search_for).replace(' ', '_')}.txt"
if value_strip('p', search_for):
    filename = f"{filename[:-4]}_{str(value_strip('p', search_for))}.txt"

if os.path.exists(os.path.join(path, filename)):
    f_exists = re.compile(r'(y.*|sure|o.*|alright)', re.I)
    if_delete = input(
        'There is already a file with the same name do you want to delete it? ')

    if f_exists.search(if_delete):
        print('Deleting...')
        for file in os.listdir(os.getcwd()):
            logging.shutdown()
            file_path = os.path.join(os.getcwd(), file)
            try:
                if os.path.basename(file) == filename:
                    send2trash.send2trash(file_path)
            except Exception as exc:
                print(f'Failed to delete {file_path}. Reason: {exc}')
    else:
        quit()

print('Creating file: AllegroBot.log...')
logging.basicConfig(filename='AllegroBot.log', level=logging.INFO, format='%(asctime)s - '
                                                                          '%(levelname)s - '
                                                                          '%(message)s')

for i in range(1, len(item_container)):
    try:
        name = item_container[i].find('a',
            class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').text
        link = item_container[i].find('a',
            class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').get('href')
        price = convert_price_to_number(item_container[i].find('span',
            class_='_1svub _lf05o').text[:-3])
        info = list(zip([item_1.text for item_1 in item_container[i].find_all('dt')],
                        [item_2.text for item_2 in item_container[i].find_all('dd')]))

        try:
            percent = item_container[i].find('span', class_='_9c44d_1uHr2').text
            discount = convert_price_to_number(item_container[i].find('span',
                class_='mpof_uk mqu1_ae _9c44d_18kEF m9qz_yp _9c44d_2BSa0 _9c44d_KrRuv').text[:-3])
            data = f"Counter: {i}\nName: {name}\nPrice: Discounted by {percent[1:]} from {discount} to {price}" \
                   f"\nAdditional info: {str(info)[1:-1]}\nLink: {link}"

        except AttributeError:
            data = (f"Counter: {i}\nName: {name}\nPrice: {price}\nAdditional info: {str(info)[1:-1]}"
                    f"\nLink: {link}")

        if price_to:
            if price <= price_to:
                item_list.append(data)
        else:
            item_list.append(data)

    # If a class of sponsored items appears
    except AttributeError as exc:
        if soup.findAll('div', {'class': '_1y62o mpof_ki _9c44d_3SD3k'}):
            logging.info(
                'The program found a sponsored item and skipped it.')
    except Exception as exc:
        logging.info(exc)

try:
    with open(filename, 'w', encoding='utf-8') as file:
        for item in item_list:
            file.write(item + os.linesep)
        print(f"Creating file: {filename}...")
except FileNotFoundError as exc:
    logging.critical(exc)
print('Done!')
