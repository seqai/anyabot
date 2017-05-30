class DataManager(object):
    def __init__(self, storage, processor, users):
        self.data = []
        self._storage = storage
        self._processor = processor
        self._users = users
        for entity in storage.data:
            self.data.append(processor.process(entity))


    def add(self, entity):
        result = self._processor.process(entity) 
        if result:
            self.data.append(result)
            self._storage.write(entity)
            return True
        return False

    def authorized(self, id):
        return id in self._processor.users

    def processable(self, entity):
        return self._processor.processable(entity)