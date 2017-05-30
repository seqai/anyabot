class DataManager(object):
    def __init__(self, storage, processor, users):
        self.data = []
        self.__storage = storage
        self.__processor = processor
        self.__users = users
        for entity in storage.data:
            self.data.append(processor.process(entity))


    def add(self, entity):
        result = self.__processor.process(entity) 
        if result:
            self.data.append(result)
            self.__storage.write(entity)
            return True
        return False

    def authorized(self, id):
        return id in self.__processor.users

    def processable(self, entity):
        return self.__processor.processable(entity)