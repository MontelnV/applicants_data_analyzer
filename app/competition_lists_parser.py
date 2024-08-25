import requests
from bs4 import BeautifulSoup
from app.database import ApplicantsORM
import re
import dateparser
from app.database import drop_app_table, create_app_table
from app.repositories import ApplicantsRepository

async def parse_it():
    url = "http://www.psu.ru/files/docs/priem-2024/bkl"
    response = requests.get(url)
    with open('priem-2024', 'wb') as file:
        file.write(response.content)
    with open('priem.html', 'r', encoding='utf-8') as file:
        content = file.read()
    faculties = []
    soup = BeautifulSoup(content, 'html.parser')
    all_articles = soup.find_all('article')
    for article in all_articles:
        study_form = article.find_all('span', {'style': 'text-transform:uppercase'})[0].text.lower()
        faculties = article.find_all('span', {'style': 'text-transform:uppercase'})[1].text
        spec = article.find_all('span', {'style': 'text-transform:uppercase'})[2].text
        agreements = article.find_all('h3')
        all_tables = article.find_all('table')
        counter = []

        for p in article.find_all('p')[2:]:
            counter.append(p.find_all('strong')[0].text.lower()) # если появится надпись "осталось", то изменить на [1]

        # блок с последней датой обновления
        last_update = article.find_all('p')[0].text.lower()
        last_update = re.sub(r"s+", " ", re.sub(r"[[^]]+]", "", re.sub(r"[а-яА-Я]+", "", last_update)))
        parsed_date = dateparser.parse(last_update, languages=['ru'])

        index = 0

        for tables in all_tables:
            all_rows = (tables.find_all('tr'))[2:]
            competitive_selection = ' '.join(re.sub(r'[.*?]', '', ((tables.find_all('tr'))[1]).text).lower().split())
            # костыль номер 2, т.к добавили квотников )))
            if competitive_selection != "общий конкурс":
                for ch_index, row in enumerate(tables.find_all('tr')):
                    if "общий конкурс" in row.text.lower():
                        all_rows = (tables.find_all('tr'))[ch_index+1:]
                        competitive_selection = "общий конкурс"
            agreement = agreements[index].text
            all_places = int(counter[index])
            users = []
            for row in all_rows:
                cells = row.find_all('td')
                number = cells[0].text.replace("\n", "").strip() if cells[0].text else None
                snils = cells[1].text.replace("\n", "").strip() if cells[1].text else None
                original_docs = True if cells[2].text.replace("\n", "").strip() else False
                original_check = True if cells[3].text.replace("\n", "").strip() else False
                exam_1 = cells[4].text.replace("\n", "").strip() if cells[4].text else None
                exam_2 = cells[5].text.replace("\n", "").strip() if cells[5].text else None
                exam_3 = cells[6].text.replace("\n", "").strip() if cells[6].text else None
                personal_achivements = cells[7].text.replace("\n", "").strip() if cells[7].text else None
                total_score = int(cells[8].text.replace("\n", "").strip() if cells[8].text else 0)
                priority = int(re.sub(r"[^\d]", "", cells[9].text.replace("\n", "").strip())) if cells[9].text else 1

                # добавляем пользователя в список
                users.append(ApplicantsORM(snils=snils, number=number, exam_1=exam_1,
                                           exam_2=exam_2, exam_3=exam_3, personal_achivements=personal_achivements,
                                           total_score=total_score, last_update_on_server=parsed_date, places=all_places))

            for user in users:
                await ApplicantsRepository.add_or_update_user(user)
            index += 1
