import os.path
from datetime import datetime
from shutil import copyfile
import json

class DataStorage(object):
    def __init__(self, file_path):
        self._file_path = file_path
        if not os.path.isfile(file_path):
            open(file_path, "w+").close()
        else:
            stamp = int(datetime.now().timestamp() * 1000)
            dest_name = file_path + "." + str(stamp) + ".bak.txt"
            copyfile(file_path, dest_name)
        with open(file_path, mode="r") as file:
            self.data = [json.loads(x.strip()) for x in file.readlines()]

    def write(self, data):
        self.data.append(data)
        with open(self._file_path, mode="a") as file:
            file.write("\n" + json.dumps(data))
