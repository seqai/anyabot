"""Anyutka bot to calculate expenses"""
import sys
import atexit
import configparser
import json

from services.DataStorage import DataStorage
from services.MessageProcessor import MessageProcessor
from services.DataManager import DataManager
from services.BotService import BotService
from services.UserService import UserService
from services.ReporterService import ReporterService
from services.ChartService import ChartService

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

TOKEN = CONFIG['DEFAULT']['ApiToken']
FILE_PATH = CONFIG['DEFAULT']['OutputFile']
USERS = CONFIG['DEFAULT']['Users']

USER_SERVICE = UserService(json.loads(USERS))
DATA_STORAGE = DataStorage(FILE_PATH)
MESSAGE_PROCESSOR = MessageProcessor(USER_SERVICE)
DATA_MANAGER = DataManager(DATA_STORAGE, MESSAGE_PROCESSOR, USER_SERVICE)
REPORTER_SERVICE = ReporterService(DATA_MANAGER, USER_SERVICE)
CHART_SERVICE = ChartService()
BOT_SERVICE = BotService(TOKEN, DATA_MANAGER, USER_SERVICE, REPORTER_SERVICE, CHART_SERVICE)
def dispose_handler():
    DATA_STORAGE.dispose()
    print("Terminating...")

atexit.register(dispose_handler)

print(REPORTER_SERVICE.report_simple())

BOT_SERVICE.run()

# Keep the program running.
while True:
    n = input('To stop enter "stop":')
    if n.strip() == 'stop':
        break

print("done")
