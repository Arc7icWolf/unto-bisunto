import time
import requests
import json
from datetime import datetime, timedelta
from logger import logger
import sys
from beem import Hive
from beem.comment import Comment
import os
import jinja2
import random
from data import contest_data
from stats import get_stats


class Config:
    def __init__(self):
        # Get credentias from Secrets
        key = os.getenv("POSTING_KEY")
        if not key:
            raise ValueError("POSTING_KEY not found")

        self.hive = Hive(keys=[key])
        self.account = "megaptera-marina"
        self.weight = 1.0

        templates = [
            "comment_0.template",
            "comment_1.template",
            "comment_2.template",
            "comment_3.template",
            "comment_4.template",
            "comment_5.template",
            "comment_6.template",
            "comment_7.template",
            "comment_8.template",
            "comment_9.template",
        ]

        chosen_template = random.choice(templates)

        self.body_template = self.load_template(chosen_template)

    def load_template(self, filename):
        template_path = os.path.join("templates", filename)
        with open(template_path, "r", encoding="utf-8") as file:
            return jinja2.Template(file.read())

    def render_body(self, target_account, author_account, info):
        return self.body_template.render(
            target_account=target_account,
            author_account=author_account,
            random_info=info,
        )


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


def cast_vote(authorperm, cfg: Config):
    voted = cfg.hive.vote(weight=cfg.weight, account=cfg.account, identifier=authorperm)
    print(f"Vote casted on {authorperm}. Sleeping for 3 sec...")
    time.sleep(3)
    return True if voted else False


def leave_comment(author, authorperm, info, cfg: Config):
    body = cfg.render_body(
        target_account=author, author_account=cfg.account, random_info=info
    )
    commented = cfg.hive.post(
        title="",
        body=body,
        author=cfg.account,
        permlink=None,
        reply_identifier=authorperm,
    )
    print(f"Comment left on {authorperm}. Sleeping for 3 sec...")
    time.sleep(3)
    return True if commented else False


def reblog(authorperm, cfg: Config):
    reblog = Comment(authorperm=authorperm, blockchain_instance=cfg.hive)
    reblogged = reblog.resteem(account=cfg.account)
    print(f"Reblogged {authorperm}. Sleeping for 3 sec...")
    time.sleep(3)
    return True if reblogged else False


# Found and check eligible posts published in the last day in the target community
def unto_bisunto_posts(session: requests.Session, cfg: Config):
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
            author = post["author"]
            permlink = post["permlink"]

            is_pinned = post.get("stats", {}).get("is_pinned", [])
            if is_pinned:
                continue

            created = post["created"]
            created_formatted = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S")
            if created_formatted < one_day:
                less_than_one_day = False
                print("No more posts less than one day older found")
                break  # Stop if post is more than 1 day old

            tags = post["json_metadata"].get("tags", [])
            if "untobisunto" not in tags:
                continue

            votes = post.get("active_votes", [])
            if any(vote["voter"] == cfg.account for vote in votes):
                continue

            """
            if author != "arc7icwolf": # for testing purpose
                continue
            """

            authorperm = f"{author}/{permlink}"

            voted = cast_vote(authorperm, cfg)
            if voted is False:
                logger.warning(f"unable to vote on {authorperm}")

            contest_data(cfg.account, session)
            info = get_stats(random.randint(1, 5))
            commented = leave_comment(author, authorperm, info, cfg)
            if commented is False:
                logger.warning(f"unable to comment on {authorperm}")

            reblogged = reblog(authorperm, cfg)
            if reblogged is False:
                logger.warning(f"unable to vote on {authorperm}")

            if voted and commented and reblogged:
                logger.info(f"{authorperm} has been upvoted, commentend and reblogged")
                print(authorperm)


def main():

    config = Config()

    try:
        with requests.Session() as session:
            unto_bisunto_posts(session, config)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"JSON decode error or missing key: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
