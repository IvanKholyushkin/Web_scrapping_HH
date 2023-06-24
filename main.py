import json
import requests
import bs4
import fake_headers
from tqdm import tqdm



def get_url(key_words):
    URL = f"https://spb.hh.ru/search/vacancy?text={key_words}&area=1&area=2&"
    return URL

def get_count_pages(URL, headers_dict):
    response = requests.get(URL, headers=headers_dict)
    soup = bs4.BeautifulSoup(response.content, "lxml")
    count_pages = int(
        soup.find("div", class_="pager")
        .find_all("span", recursive=False)[-1]
        .find("a")
        .find("span")
        .text
    )
    return count_pages

def get_vacancies(URL, count_pages):
    for _ in tqdm(range(0, count_pages)):
        response = requests.get(URL, headers=headers_dict)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        data = json.loads(
            soup.find("template", attrs={"id": "HH-Lux-InitialState"}).text
        )
        for vacancy in data["vacancySearchResult"]["vacancies"]:
            position = vacancy["name"]
            company_name = vacancy["company"]["name"]
            city_name = vacancy["area"]["name"]
            link = vacancy["links"]["desktop"]
            salary = vacancy["compensation"]
            if len(salary) == 4 and salary.get("gross") is False:
                salary = (
                    f'от {salary.get("from", "")} до {salary.get("to", "")} {salary.get("currencyCode")}'
                    f' на руки'
                )
            elif len(salary) == 4 and salary.get("gross") is True:
                salary = (
                    f'от {salary.get("from", "")} до {salary.get("to", "")} {salary.get("currencyCode")}' 
                    f'до вычета налогов'
                )
            elif len(salary) == 3 and salary.get("from", "") == "" and salary.get("gross") is False:
                salary = (
                    f'до {salary.get("to", "")} {salary.get("currencyCode")} на руки'
                )
            elif len(salary) == 3 and salary.get("to", "") == "" and salary.get("gross") is True:
                salary = (
                    f'от {salary.get("from", "")} {salary.get("currencyCode")} до вычета налогов'
                )
            elif len(salary) == 3 and salary.get("from", "") == "" and salary.get("gross") is True:
                salary = (
                    f'до {salary.get("to", "")} {salary.get("currencyCode")} на руки'
                )
            elif len(salary) == 3 and salary.get("to", "") == "" and salary.get("gross") is False:
                salary = f'от {salary.get("from", "")} {salary.get("currencyCode")} до вычета налогов'
            elif len(salary) == 1:
                salary = "Зарплата не указана"
            resulting_list.append(
                {
                    "Ссылка": link,
                    "Должность": position,
                    "Компания": company_name,
                    "Город": city_name,
                    "Зарплата": salary,
                }
            )


if __name__ == "__main__":
    resulting_list = []
    headers = fake_headers.Headers(browser="firefox", os="win")
    headers_dict = headers.generate()
    URL = get_url("+".join(input("Введите ключевые слова ").split()))
    try:
        count_pages = get_count_pages(URL, headers_dict)
    except AttributeError:
        count_pages = 1
    get_vacancies(URL, count_pages)
    with open("vacancy.json", "w") as outfile:
        json.dump(resulting_list, outfile, indent=6, ensure_ascii=False)
    print(f"Было загруженно {len(resulting_list)} вакансий")

