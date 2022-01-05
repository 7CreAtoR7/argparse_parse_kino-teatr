import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
import pymorphy2


def parse_page_actors_s(page_number):
    """Function parses actro's info whose names start with the letter <С>
    from https://www.kino-teatr.ru/kino/acter/w/ros/s/a1 first 5 pages"""

    months = {'январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь',
              'декабрь'}
    morph = pymorphy2.MorphAnalyzer()
    # set of months to determine is there any birthday in text
    params = {
        "User-Agent": UserAgent().chrome,
        "Accept-Encoding": "*",
        "Connection": "keep-alive"
    }  # extra params => looks like person's request

    url = f"https://www.kino-teatr.ru/kino/acter/w/ros/s/a{page_number}"  # page number to parse
    response = requests.get(url, params=params)
    if response.__bool__():
        html = response.text  # send query to get html content of web page

        soup = BeautifulSoup(html, 'lxml')
        result_data = []  # list of dictionaries with actor's info
        for actor in soup.find_all('div', attrs={'class': 'list_item'}):
            # found tag, where we can get photo, name and birthday
            dict_people = {
                'Photo': '',
                'Name': '',
                'Birthday': ''
            }  # dict_people - dictionary with user's info
            for actor_info in actor.find_all('div', attrs={'class': 'list_item_photo'}):
                actor_name = actor_info.findAll('img')[0]['alt']  # get actor's name
                actor_photo = f"https://www.kino-teatr.ru{actor_info.findAll('img')[0]['src']}"
                dict_people['Photo'] = actor_photo  # get actor's photo specifying the img tag
                dict_people['Name'] = actor_name  # indicate the corresponding value

            for actor_info_birthday in actor.find_all('div', attrs={'itemprop': 'description'}):
                actor_birthday = actor_info_birthday.text.strip().split('\n')[0].strip('\r').split(' ')
                first_line_of_text_normalized = list(map(lambda x: morph.parse(x)[0].normal_form, actor_birthday))
                # all words are normalized:
                # ['Родилась', '17', 'ноября', '1980', 'года.'] ---> ['родиться', '17', 'ноябрь', '1980', 'года.']
                # let's check is there any month in person's birthday:
                if any([month in first_line_of_text_normalized for month in months]) or 'родиться' in \
                        first_line_of_text_normalized:
                    # is there birthday info in first line of text info?
                    # if text contains the word "родиться", so we will take it
                    dict_people['Birthday'] = ' '.join(actor_birthday)
                else:  # or we have no info about actor's birthday
                    dict_people['Birthday'] = "There is no info"

            if not dict_people['Birthday']:
                dict_people['Birthday'] = "There is no info"

            result_data.append(dict_people)
        return result_data
    else:
        print("Query error:")
        print("Https status:", response.status_code, "(", response.reason, ")")


def main(count_pages):
    all_actors = []  # list of dictionaries
    with open("actors_info.json", 'w', encoding='utf8') as file:
        for i in range(1, count_pages + 1):  # visit every link
            print(f"The page number {i} is parsed")
            list_of_dict_current_page = parse_page_actors_s(i)
            all_actors.extend(list_of_dict_current_page)  # save list info in json
        json.dump(all_actors, file, indent=4, ensure_ascii=False)
    print(f"Done! Find actors_info.json file to check actor's info")


if __name__ == '__main__':
    main(5)
