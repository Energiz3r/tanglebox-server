class BasicQueue:
    queue: list

    def __init__(self):
        self.queue = []

    def add(self, id):
        self.queue.append(id)

    def getLength(self):
        return len(self.queue)

    def complete(self, id):
        self.queue.remove(id)

    def check_ready(self, id):
        return self.queue[0] == id
