import time
import re
from io import BytesIO
import telepot
from telepot.loop import MessageLoop

class BotService(object):
    def __init__(self, token, manager, users, reporter, charting):
        self.__token = token
        self.__manager = manager
        self.__users = users
        self.__reporter = reporter
        self.__charting = charting
        self.__bot = telepot.Bot(self.__token)

    def run(self):
        MessageLoop(self.__bot, self.__handle).run_as_thread()
        print('Listening ...')

    def __handle(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        if not self.__users.authorized(msg["from"]["id"]):
            return

        print(msg)

        bot_command = self.__get_command(msg)

        if bot_command:
            arguments = self.__get_command_arguments(msg["text"])
            self.__process_command(bot_command, arguments, chat_id)
        elif self.__manager.processable(msg):
            if self.__manager.add(msg):
                pass
            else:
                self.__bot.sendMessage(chat_id, "Invalid data format")

    def __process_command(self, command, arguments, chat_id):
        def genLine(line):
            return f"{line['name']}: {line['sum']}"
        def genSeriesLine(line):
            return "\t".join([genLine(subline) for subline in line])

        print("Command", command)
        print("Arguments", arguments)
        if command == "report":
            report = self.__reporter.report(arguments)
            response = "\n".join([genLine(line) for line in report])
            self.__bot.sendMessage(chat_id, response)
        elif command == "series":
            report = self.__reporter.report_series(arguments)
            response = "\n".join([f"{line['date'].strftime('%d.%m.%Y')}\t{genSeriesLine(line['values'])}" for line in report])
            self.__bot.sendMessage(chat_id, response)
        elif command == "pie":
            report = self.__reporter.report(arguments)
            data = {
                "labels": [x["name"] for x in report],
                "values": [x["sum"] for x in report]
            }
            image = BytesIO()
            self.__charting.plot_pie(data, image)
            image.seek(0)
            self.__bot.sendPhoto(chat_id, image)
            image.close()
        elif command == "bars":
            report = self.__reporter.report_series(arguments)
            labels = [x["name"] for x in report[0]["values"]]
            data = {
                "x": [x["date"].strftime("%d.%m") for x in report],
                "labels": labels,
                "values": map(list, zip(*[[y["sum"] for y in x["values"]] for x in report]))
            }
            image = BytesIO()
            self.__charting.plot_bars(data, image)
            image.seek(0)
            self.__bot.sendPhoto(chat_id, image)
            image.close()

    @staticmethod
    def __get_command_arguments(text):
        def splitValues(word):
            tokens = word.split(":", 1)
            values = None
            if len(tokens) > 1:
                values = tokens[1].split(":")
            return {
                "a": tokens[0],
                "v": values
            }
        words = re.sub(" +", " ", text.strip().lower()).split(" ")
        return {e["a"]: e["v"] for e in [splitValues(word) for word in words[1:]]}

    @staticmethod
    def __get_command(msg):
        if not "text" in msg:
            return None
        if not "entities" in msg:
            return None
        entities = msg["entities"]
        text = msg["text"]
        if entities[0]["type"] != "bot_command":
            return None
        return text[entities[0]["offset"]+1:entities[0]["length"]].lower()

