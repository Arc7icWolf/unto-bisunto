import os
import csv
import sys
from collections import defaultdict


def total_prizes(reader: csv.DictReader) -> str:
    total = 0
    for row in reader:
        total += float(row["amount"].split()[0])

    return (
        f"Il contest **Unto&Bisunto** ha distribuito premi "
        f"per un totale di {total:.3f} HIVE? Impressionante!"
    )


def all_winners(reader: csv.DictReader) -> list:
    totals = defaultdict(float)

    for row in reader:
        to = row["to"]
        totals[to] += float(row["amount"].split()[0])

    winners = [{"to": to, "amount": round(amount, 3)} for to, amount in totals.items()]
    return sorted(winners, key=lambda x: x["amount"], reverse=True)


def most_rewarded(reader: csv.DictReader) -> str:
    winners = all_winners(reader)
    return (
        f"L'utente più premiato del contest **Unto&Bisunto** è... @{winners[0]['to']}, "
        f"con {winners[0]['amount']} HIVE vinti! Congratulazioni :)"
    )


def second_most_rewarded(reader: csv.DictReader) -> str:
    winners = all_winners(reader)
    return (
        f"Sai chi è il secondo utente più premiato del contest **Unto&Bisunto**? E' @{winners[1]['to']}, "
        f"con {winners[1]['amount']} HIVE portati a casa! Complimenti :)"
    )


def third_most_rewarded(reader: csv.DictReader) -> str:
    winners = all_winners(reader)
    return (
        f"Il terzo maggior vincitore del contest **Unto&Bisunto** è @{winners[2]['to']}, "
        f"grazie a {winners[2]['amount']} HIVE vinti! Un grandissimo risultato :)"
    )


def participants(reader: csv.DictReader) -> str:
    winners = all_winners(reader)
    return (
        f"Dalla sua nascita il contest **Unto&Bisunto** ha visto la partecipazione di {len(winners)} utenti... "
        f"e tu sei uno di loro!"
    )


def get_stats(num: int) -> str:
    if os.path.exists("winners.csv"):
        with open("winners.csv", "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            if not reader:
                return ""
            match num:
                case 1:
                    return total_prizes(reader)
                case 2:
                    return most_rewarded(reader)
                case 3:
                    return second_most_rewarded(reader)
                case 4:
                    return third_most_rewarded(reader)
                case 5:
                    return participants(reader)
                case _:
                    return ""

    else:
        return ""


if __name__ == "__main__":
    num = 5
    get_stats(num)
