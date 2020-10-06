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
product_list_counter = []
if len(sys.argv) > 1:
    search_for = ' '.join(sys.argv[1:])

path = os.path.join(os.getcwd(), 'AllegroBot')
img_path = os.path.join(path, 'Pictures')

# Regular expression that strips the price from the terminal
# and also removes the '-p number' from the search_for variable.
price_regex = re.compile(r'(-p\s?)(\d+)', re.I)
if price_regex.search(str(search_for)):
    price_below = float(price_regex.search(str(search_for)).group(2))
    search_for = search_for.replace(
        price_regex.search(str(search_for)).group(), '').strip()

# Part of code that scrapes the html from the website.
url = 'https://allegro.pl/listing?string='
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/'
                         '537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}
page = requests.get(url + search_for, headers=headers)

soup = BeautifulSoup(page.text, features='lxml')

item_container = soup.findAll('div', {'class': 'mpof_ki myre_zn _9c44d_1Hxbq'})
img_container = soup.findAll(
    'div', {'class': 'mpof_ki myre_zn m389_6m mse2_56 _9c44d_2Tos9'})

# Statement that checks if any items are found.
if not len(item_container) < 1:
    if not os.path.exists(path):
        print(f'\nCreating a folder {os.path.basename(path)}...')
        os.mkdir(path)
    os.chdir(path)
    sleep(1)

    filename = f"allegro_{search_for.replace(' ', '_')}.txt"

    # If the file already exists, user can decide if he wants to delete it or not.
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
                    # Used send2trash package which speaks for its name and sends the files to the Recycle Bin.
                    send2trash.send2trash(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        else:
            quit()

    print('\nCreating file: AllegroBot.log...')
    sleep(1)
    # Creating a logging file which saves all errors that the program ran into.
    logging.basicConfig(filename='AllegroBot.log', level=logging.INFO, format='%(asctime)s - '
                                                                              '%(levelname)s - '
                                                                              '%(''message)s')

    for i in range(len(item_container)):
        try:
            price = item_container[i].find(
                'span', class_='_1svub _lf05o').text[:-3]

            # Part that is responsible for changing e.g. a str of 1 122,99 to a float of 1122.99
            rep = {',': '.', ' ': ''}
            rep = dict((re.escape(k), v) for k, v in rep.items())

            pattern = re.compile('|'.join(rep.keys()))
            price = float(pattern.sub(
                lambda m: rep[re.escape(m.group(0))], price))

            # Variables that contain specific information about a product.
            name = item_container[i].find(
                'a', class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').text
            link = item_container[i].find(
                'a', class_='_w7z6o _uj8z7 meqh_en mpof_z0 mqu1_16 _9c44d_2vTdY').get('href')

            # List of Tuples that contain additional info about the product, e.g. ('matrix': '30 inches').
            info = list(zip([item_1.text for item_1 in item_container[i].find_all('dt')],
                            [item_2.text for item_2 in item_container[i].find_all('dd')]))
            data = f"Counter: {i}\nName: {name}\nPrice: {price}\nAdditional info: {str(info)[1:-1]}\nLink: {link}"

            product_list_counter.append(str(i))

            # If the '-p' is passed into the terminal
            # Append only cheaper or the same price as passed
            try:
                if price <= price_below:
                    item_list.append(data)
            except Exception as exc:
                item_list.append(data)

        # The class passed in the if statement is a class for sponsored items which we don't want
        # So whenever the program runs into that div it skips it and logs the information to the .log file
        except AttributeError as exc:
            if soup.findAll('div', {'class': '_1y62o mpof_ki _9c44d_3SD3k'}):
                logging.info(
                    'The program found a sponsored item and skipped it.')
        except Exception as exc:
            logging.info(exc)

    print('\nSaving images...')
    for i in range(len(img_container)):
        try:
            img_src = img_container[i].img.get('data-src')

            # Creating a folder for the photos and using os.chdir() to change the current working directory.
            if not os.path.exists(img_path):
                os.mkdir(img_path)

            os.chdir(img_path)

            # Requesting an image source and saving it using 'wb' - write binary File mode
            if str(i) in product_list_counter:
                res = requests.get(img_src)
                image_file = open(os.path.join(
                    os.getcwd(), str(i) + '.jpg'), 'wb')

                # Iterating over the response with 100000 bytes each time and saving it as a image.
                for chunk in res.iter_content(100000):
                    image_file.write(chunk)

                image_file.close()

            os.chdir('..')

        except Exception as exc:
            logging.info(exc)

    # Creating a .txt file for the results.
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

# TODO: Fix the img saving part.
