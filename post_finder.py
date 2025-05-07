import time
import requests
import json
from datetime import datetime, timedelta
import re
import logging
import sys
from beem import Hive
import json


HIVE = Hive(keys=['xxxxxxxxxxxxx'])
ACCOUNT = "xxxxx"
WEIGTH = 100.0
BODY = "Upvote e reblog!"


# logger
def get_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("post_finder.log", mode="a")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = get_logger()


# Send request, get response, return decoded JSON response
def get_response(data, session: requests.Session):
    urls = [
        "https://api.deathwing.me",
        "https://api.hive.blog",
        "https://hive-api.arcange.eu",
        "https://api.openhive.network"
    ]
    for url in urls:
        request = requests.Request("POST", url=url, data=data).prepare()
        response_json = session.send(request, allow_redirects=False)
        if response_json.status_code == 502:
            continue
        response = response_json.json().get("result", [])
        if len(response) == 0:
            logger.warning(f"{response_json.json()} from this {data}")
        return response


def cast_vote(authorperm):
    HIVE.vote(weight=WEIGTH, account=ACCOUNT, identifier=authorperm)
    print(f"Vote casted on {authorperm}")


def leave_comment(authorperm):
    HIVE.post(
        body=BODY,
        author=ACCOUNT,
        permlink=authorperm,
        reply_identifier=None,
    )
    print(f"Comment left on {permlink}")


def reblog(authorperm):
    HIVE.resteem(identifier=authorperm, account=ACCOUNT)
    print(f"Reblogged {authorperm}")


# Found and check eligible posts published in the last 7 days in the target community
def unto_bisunto_posts(session: requests.Session):
    today = datetime.now()
    one_day = today - timedelta(days=1, hours=1)

    less_than_one_day = True

    author = ""
    permlink = ""


    while less_than_one_day:
        # Get posts published in the target community
        data = (
            f'{{"jsonrpc":"2.0", "method":"bridge.get_ranked_posts", '
            f'"params":{{"sort":"created","tag":"hive-146620","observer":"", '
            f'"limit": 100, "start_author":"{author}", "start_permlink":"{permlink}"}}, '
            f'"id":1}}'
        )
        posts = get_response(data, session)
        for post in posts:
            is_pinned = post.get("stats", {}).get("is_pinned", [])
            tags = post['json_metadata']['tags']
            created = post["created"]
            author = post["author"]
            permlink = post["permlink"]

            if is_pinned:
                continue

            if "untobisunto" not in tags:
                continue

            created_formatted = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S")
            if created_formatted < one_day:
                less_than_one_day = False
                print("No more posts less than one day older found")
                break  # Stop if post is more than 1 day old

            authorperm = f"{author}/{permlink}"

            cast_vote(authorperm)
            leave_comment(authorperm)
            reblog(authorperm)
      
            print(post["title"])
            continue


def main():
    try:
        with requests.Session() as session:
            unto_bisunto_posts(session)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"JSON decode error or missing key: {e}")
    #except Exception as e:
    #    logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
