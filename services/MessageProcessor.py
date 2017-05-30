from datetime import datetime
from functools import reduce
import re
from helpers.helpers import try_parse_date

CURRENCIES = {
    "rub": ["rub","руб","р","руб.","р.","рубль","рублей" ],
    "usd": ["usd","$" ],
    "eur": ["eur"],
}

KEYTAG = "#расходы"

class MessageProcessor(object):
    def __init__(self, users):
        self.__users = users

    def processable(self, entity):
        if not "text" in entity:
            return False
        if not "entities" in entity:
            return False
        entities = entity["entities"]
        text = entity["text"]
        if entities[0]["type"] != "hashtag":
            return False
        if text[entities[0]["offset"]:entities[0]["length"]].lower() != KEYTAG:
            return False
        return True

    def process(self, entity):
        user = entity["from"]["id"]
        date = entity["date"]
        category = None
        subproducts = None
        price = None
        currency = "rub"
        if not self.__users.authorized(user):
            return None

        tokens = self.__tokenize(entity["text"])
        if tokens:
            if tokens["products"][0]:
                category = tokens["products"][0]
            if len(tokens["products"]) > 1:
                subproducts = tokens["products"][1:]

            if len(tokens["mentions"]) > 0:
                if len(tokens["mentions"]) == 1 and self.__users.aliases[tokens["mentions"][0]]:
                    user = self.__users.aliases[tokens["mentions"][0]]
                else:
                    return None

            for data in tokens["data"]:
                if self.__is_number(data):
                    if price:
                        return None
                    price = float(data)
                    continue

                parsed_date = try_parse_date(data)
                if parsed_date:
                    date = parsed_date
                    continue

                for key, value in CURRENCIES.items():
                    if data in value:
                        currency = key
                        break

            if user and date and category and price and currency:
                print((user, datetime.fromtimestamp(date).isoformat(), category, subproducts, price, currency))
                return {
                    "user": user,
                    "date": date,
                    "category": category,
                    "subproducts": subproducts,
                    "price": price,
                    "currency": currency
                }

        return None

    @staticmethod
    def __tokenize(text):
        def categorize (lists, el):
            if el[0] == "#":
                lists["products"].append(el[1:])
            elif el[0] == "@":
                lists["mentions"].append(el[1:])
            else:
                lists["data"].append(el)
            return lists

        words = re.sub(" +", " ", text.strip().lower()).split(" ")
        if len(words) < 2 or words[0] != KEYTAG:
            return

        wordlist = reduce(categorize, words[1:], {"products":[],"mentions":[],"data":[]})

        return wordlist

    @staticmethod
    def __is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False