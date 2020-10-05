#  AllegroBot.py - A quick Bot that searches for the items you want to buy :-)
#  Adding a '-p' followed by a number filters items that cost less or the same.

import sys
import os
import re
import send2trash
import logging
import requests
from bs4 import BeautifulSoup
from time import sleep

search_for = ''
item_list = []
if len(sys.argv) > 1:
    search_for = ' '.join(sys.argv[1:])

path = os.path.join(os.getcwd(), 'AllegroBot')
img_path = os.path.join(path, 'Pictures')

price_regex = re.compile(r'(-p\s?)(\d+)', re.I)
if price_regex.search(str(search_for)):
    price_below = float(price_regex.search(str(search_for)).group(2))
    search_for = search_for.replace(
        price_regex.search(str(search_for)).group(), '').strip()

url = 'https://allegro.pl/listing?string='
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
page = requests.get(url + search_for, headers=headers)

soup = BeautifulSoup(page.text, features='lxml')

item_container = soup.findAll('div', {'class': 'mpof_ki myre_zn _9c44d_1Hxbq'})
img_container = soup.findAll(
    'div', {'class': 'mpof_ki myre_zn m389_6m m09p_k4 mse2_56 _9c44d_2Tos9'})

if not len(item_container) < 1:
    if not os.path.exists(path):
        print(f'\nCreating a folder {os.path.basename(path)}...')
        os.mkdir(path)
    os.chdir(path)
    sleep(1)

    filename = f"allegro_{search_for.replace(' ', '_')}.txt"

    if os.path.exists(os.path.join(path, filename)):
        f_exists = re.compile(r'(y.*|sure|ok|okay|alright)', re.I)
        if_delete = input(
            'There is already a file with the same name do you want to delete it? ')

        if f_exists.search(if_delete):
            print('\nDeleting...')
            sleep(1)
            for file in os.listdir(os.getcwd()):
                logging.shutdown()
                file_path = os.path.join(os.getcwd(), file)
                try:
                    send2trash.send2trash(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        else:
            quit()

    print('\nCreating file: AllegroBot.log...')
    sleep(1)
    logging.basicConfig(filename='AllegroBot.log', level=logging.INFO, format='%(asctime)s - '
                                                                              '%(levelname)s - '
                                                                              '%(''message)s')

    print('\nSaving images...')
    for i in range(len(item_container)):
        try:
            price = item_container[i].find(
                'span', class_='_1svub _lf05o').text[:-3]

            rep = {',': '.', ' ': ''}
            rep = dict((re.escape(k), v) for k, v in rep.items())

            pattern = re.compile('|'.join(rep.keys()))
            price = float(pattern.sub(
                lambda m: rep[re.escape(m.group(0))], price))

            name = item_container[i].find(
                'a', class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').text
            link = item_container[i].find(
                'a', class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').get('href')
            img_src = img_container[i].img.get('data-src')

            info = list(zip([item_1.text for item_1 in item_container[i].find_all('dt')],
                            [item_2.text for item_2 in item_container[i].find_all('dd')]))
            data = f"Counter: {i}\nName: {name}\nPrice: {price}\nAdditional info: {str(info)[1:-1]}\nLink: {link}"

            if not os.path.exists(img_path):
                os.mkdir(img_path)

            os.chdir(img_path)

            res = requests.get(img_src)
            image_file = open(os.path.join(os.getcwd(), str(i) + '.jpg'), 'wb')

            for chunk in res.iter_content(100000):
                image_file.write(chunk)

            image_file.close()

            os.chdir('..')

            try:
                if price <= price_below:
                    item_list.append(data)
            except Exception as exc:
                logging.info(exc)
                item_list.append(data)

        except AttributeError as exc:
            if soup.findAll('div', {'class': '_1y62o mpof_ki _9c44d_3SD3k'}):
                logging.info(
                    'The program found a sponsored item and skipped it.')
        except Exception as exc:
            logging.info(exc)

    sleep(1)
    try:
        with open(filename, 'w') as file:
            for item in item_list:
                file.write(item + os.linesep)
            print(f"\nCreating a file: {filename}...")
            sleep(1)
    except FileNotFoundError as exc:
        logging.critical(exc)
    print('\nDone!')

else:
    print('\nNo items match your search.')
