import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import Union
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def load_info() -> Union[dict, str]:
    """
    Парсинг открытых данных в виде ссылок на excel таблицы
    с сайта Федеральной службы государственной статистики.
    Регионы России. Социально-экономические показатели.
    """

    main_url = "https://rosstat.gov.ru/"
    result_dict = {}
    # получаем ссылку на страницу с таблицами
    url4link = f"{main_url}folder/210/document/13204"
    response4link = requests.get(url4link)
    status4link = response4link.status_code
    if status4link == 200:
        try:
            soup4link = BeautifulSoup(response4link.content, "html.parser")
            # актуальность данных на странице
            info = soup4link.find("div", class_="document-list__item-info")
            actual_dt = info.text.split(", ")[-1]
            result_dict["actual_date"] = actual_dt
            # находим класс с указанием на "Таблицы в формате Excel"
            tables4link = soup4link.select("div.document-list__item-link a.btn")
            for link in tables4link:
                l = link["href"]
                if l.endswith("htm"):
                    tables_url = l
        except Exception as error:
            return f"{error=}"
    else:
        return f"Не смогли получить доступ к странице с таблицами: {status4link}"
    sleep(3)
    url = f"{main_url}{tables_url}"
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        try:
            soup = BeautifulSoup(response.content, "html.parser")
            # находим таблицу с ссылками на файлы
            tables = soup.find_all("table", class_="MsoNormalTable")
            # находим все ссылки на excel файлы и их описания в теге href
            for table in tables:
                links = table.find_all("a", href=True)
                for link in links:
                    l = link["href"]
                    if l.endswith("xlsx"):
                        key = " ".join(link.get_text().split())
                        result_dict[key] = l
        except Exception as error:
            return f"{error=}"
    else:
        return f"Ошибка доступа к ресурсу: {status}"
    print(f"Актуальность данных: {actual_dt}")
    return result_dict


if __name__ == "__main__":
    load_info()
