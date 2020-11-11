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

path = os.path.join(os.getcwd(), 'AllegroBot')

# TODO -> implement an option for multiple pages, not just one.
if value_strip('P', search_for):
    pass

# Part of code that scrapes the html from the website.
url = 'https://allegro.pl/listing?string='
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
page = requests.get(url + search_strip(search_for), headers=headers)

soup = BeautifulSoup(page.text, features='lxml')

item_container = soup.findAll('div', {'class': 'mpof_ki myre_zn _9c44d_1Hxbq'})

# Statement that checks if any items are found.
if len(item_container) != 0:
    if not os.path.exists(path):
        print(f'Creating folder {os.path.basename(path)}...')
        os.mkdir(path)
    os.chdir(path)
else:
    print('No items match your search.')
    quit()

if value_strip('p', search_for):
    filename = f"allegro_{search_strip(search_for).replace(' ', '_')}_{str(value_strip('p', search_for))}.txt"
else:
    filename = f"allegro_{search_strip(search_for).replace(' ', '_')}.txt"

# If the file already exists, user can decide if he wants to delete it or not.
if os.path.exists(os.path.join(path, filename)):
    f_exists = re.compile(r'(y.*|sure|o.*|alright)', re.I)
    if_delete = input(
        'There is already a file with the same name do you want to delete it? ')

    # !!! Be careful at this moment if you want to delete a file it will wipe the whole AllegroBot folder. !!!
    if f_exists.search(if_delete):
        print('Deleting...')
        for file in os.listdir(os.getcwd()):
            logging.shutdown()
            file_path = os.path.join(os.getcwd(), file)
            try:
                # Used send2trash package which speaks for its name and sends the files to the Recycle Bin.
                send2trash.send2trash(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
    else:
        quit()

print('Creating file: AllegroBot.log...')
# Creating a logging file which saves all errors that the program ran into.
logging.basicConfig(filename='AllegroBot.log', level=logging.INFO, format='%(asctime)s - '
                                                                          '%(levelname)s - '
                                                                          '%(''message)s')

for i in range(1, len(item_container)):
    try:
        # Variables that contain specific information about a product.
        name = item_container[i].find(
            'a', class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').text
        link = item_container[i].find(
            'a', class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').get('href')
        price = convert_price_to_number(item_container[i].find(
            'span', class_='_1svub _lf05o').text[:-3])
        price_below = value_strip('p', search_for)

        # List of Tuples that contain additional info about the product, e.g. ('matrix': '30 inches').
        info = list(zip([item_1.text for item_1 in item_container[i].find_all('dt')],
                        [item_2.text for item_2 in item_container[i].find_all('dd')]))

        try:
            percent = item_container[i].find('span', class_='_9c44d_1uHr2').text
            discount = convert_price_to_number(item_container[i].find(
                'span', class_='mpof_uk mqu1_ae _9c44d_18kEF m9qz_yp _9c44d_2BSa0 _9c44d_KrRuv').text[:-3])

            data = f"Counter: {i}\nName: {name}\nPrice: Discounted by {percent[1:]} from {discount} to {price}" \
                   f"\nAdditional info: {str(info)[1:-1]}\nLink: {link}"

        except AttributeError:
            data = (f"Counter: {i}\nName: {name}\nPrice: {price}\nAdditional info: {str(info)[1:-1]}"
                    f"\nLink: {link}")

        if price_below:
            if price <= price_below:
                item_list.append(data)
        else:
            item_list.append(data)

    # The class passed in the if statement is a class for sponsored items which we don't want
    # So whenever the program runs into that div it skips it and logs the information to the .log file
    except AttributeError as exc:
        if soup.findAll('div', {'class': '_1y62o mpof_ki _9c44d_3SD3k'}):
            logging.info(
                'The program found a sponsored item and skipped it.')
    except Exception as exc:
        logging.info(exc)

# Creating a .txt file for the results.
try:
    with open(filename, 'w', encoding='utf-8') as file:
        for item in item_list:
            file.write(item + os.linesep)
        print(f"Creating file: {filename}...")
except FileNotFoundError as exc:
    logging.critical(exc)
print('Done!')
