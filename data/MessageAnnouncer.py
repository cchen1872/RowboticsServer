import queue

class MessageAnnouncer:
# Can send queue id to user and have them send it with the close request
# Only way to really have collection of queues (dictionary)
    def __init__(self):
        self.listener = None
        self.user = None

    def listen(self, username):
        self.user = username
        q = queue.Queue(maxsize=50)
        self.listeners = q
        return q

    def announce(self, msg):
        try:
            self.listeners.put_nowait(msg)
        except queue.Full:
            del self.listeners
    
    def close(self):
        # call function, send summary to mongo db
        self.user = None
        q = None
    
    def isOpen(self):
        return self.listener is not None