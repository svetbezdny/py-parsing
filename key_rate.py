import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import perf_counter
from functools import wraps
from typing import Any, Callable


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    "Функция для измерения выполнения кода"

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        time_start = perf_counter()
        res = func(*args, **kwargs)
        time_end = perf_counter() - time_start
        print(f"Функция {func.__name__} отработала за {time_end:.3f} секунд")
        return res

    return wrapper


@timer
def main() -> None:
    "Парсинг ключевой ставки Банка России"

    print("Старт...")
    current_date = datetime.now().date()
    current_date_format = f'{current_date.day}.{str(current_date.month).rjust(2, "0")}.{current_date.year}'

    url = f"https://www.cbr.ru/hd_base/keyrate/?UniDbQuery.Posted=True&UniDbQuery.From=17.09.2013&UniDbQuery.To={current_date_format}"
    response = requests.get(url)

    print(f"Статус: {response.status_code}...")
    try:

        soup = BeautifulSoup(response.text, "lxml")

        df = pd.DataFrame(columns=["date", "rate"])

        for i in soup.select_one(".data"):

            string = str(i).split()
            if string and all(
                ["дата" not in string[1].lower(), "ставка" not in string[2].lower()]
            ):
                dt = datetime.strptime(string[1].strip("<td>/"), "%d.%m.%Y")
                rt = float(string[2].strip("<td>/").replace(",", "."))
                row = {"date": dt, "rate": rt}
                df.loc[len(df)] = row

        df = df.sort_values(by="date")

        df.insert(
            loc=1,
            column="prev",
            value=pd.to_datetime(df["date"].shift(-1).fillna(current_date)).dt.date,
        )
        df["date"] = pd.to_datetime(df["date"]).dt.date

        df.to_excel("key_rate.xlsx", index=False, header=False, float_format="%.1f")

        print(f"Данные загружены и сохранены. {os.path.abspath('key_rate.xlsx')}")
    except requests.exceptions.RequestException as ex:
        print(f"Ошибка: {ex}")


if __name__ == "__main__":
    main()
