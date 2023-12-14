class BasicQueue:
    queue: list

    def __init__(self):
        self.queue = []

    def add(self, id):
        self.queue.append(id)

    def complete(self, id):
        self.queue.remove(id)

    def check_ready(self, id):
        return self.queue[0] == id
