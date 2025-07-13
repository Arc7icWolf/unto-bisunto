import requests
import json
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


def transfers(author, session: requests.Session):
    num = 1000
    while True:
        # Get all custom operations from target account, poll votes included
        data = (
            f'{{"jsonrpc":"2.0", "method":"condenser_api.get_account_history", '
            f'"params":["{author}", {num}, 1000], "id":1}}'
        )
        transfers = get_response(data, session)

        if not transfers:
            return

        for transfer in transfers:
            tx_data = transfer[1]['op']        
            if tx_data[0] == "transfer":
                print(tx_data[1])
        
        num += 1000


if __name__ == "__main__":
    author = "balaenoptera"
    try:
        with requests.Session() as session:
            transfers(author, session)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"JSON decode error or missing key: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")