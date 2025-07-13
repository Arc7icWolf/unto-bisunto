import requests
import json
import csv
import os
from logger import logger
import sys


# Send request, get response, return decoded JSON response
def get_response(data, session: requests.Session):
    urls = [
        "https://api.deathwing.me",
        "https://api.hive.blog",
        "https://hive-api.arcange.eu",
        "https://api.openhive.network",
    ]
    for url in urls:
        request = requests.Request("POST", url=url, data=data).prepare()
        response_json = session.send(request, allow_redirects=False)
        if response_json.status_code == 502:
            continue
        response = response_json.json().get("result", [])
        if len(response) == 0 or not response:
            logger.warning(f"{response_json.json()} from this {data}")
            return []
        return response


def transfers(author, num, session: requests.Session):
    winners_list = []
    while True:
        data = (
            f'{{"jsonrpc":"2.0", "method":"condenser_api.get_account_history", '
            f'"params":["{author}", {num}, 1000], "id":1}}'
        )
        transfers = get_response(data, session)

        if not transfers:
            return winners_list

        for transfer in transfers:
            tx_data = transfer[1]["op"]
            if tx_data[0] == "transfer" and tx_data[1]["from"] == author:
                print(tx_data[1])
                if tx_data[1]["to"] == "fedesox":
                    continue
                winners_list.append(
                    {
                        "num": transfer[0],
                        "to": tx_data[1]["to"],
                        "amount": tx_data[1]["amount"],
                    }
                )
                return winners_list

        num += 1000


def save_winners(winners):
    filename = "winners.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["num", "to", "amount"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for winner in winners:
            writer.writerow(winner)


def contest_data(author, session):
    num = 1000
    if os.path.exists("winners.csv"):
        with open("winners.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            if rows:
                num += int(rows[-1]["num"])

    winners = transfers(author, num, session)
    save_winners(winners)


if __name__ == "__main__":
    author = "balaenoptera"
    try:
        with requests.Session() as session:
            contest_data(author, session)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"JSON decode error or missing key: {e}")
