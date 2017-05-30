import os.path
from datetime import datetime
from shutil import copyfile
import json

class DataStorage(object):
    def __init__(self, file_path):
        if not os.path.isfile(file_path):
            open(file_path, "w+").close()
        else:
            stamp = int(datetime.now().timestamp() * 1000)
            dest_name = file_path + "." + str(stamp) + ".bak.txt"
            copyfile(file_path, dest_name)
        self.__file = open(file_path, mode="r+")
        self.data = [json.loads(x.strip()) for x in self.__file.readlines()]

    def write(self, data):
        self.data.append(data)
        self.__file.write("\n" + json.dumps(data))

    def dispose(self):
        self.__file.close()

