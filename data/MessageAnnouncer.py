import queue
from threading import Lock, Condition

class MessageAnnouncer:
# Can send queue id to user and have them send it with the close request
# Only way to really have collection of queues (dictionary)
    def __init__(self):
        self.listener = None
        self.user = None
        self.lock = Lock()
        self.empty_cv = Condition(self.lock)
        self.close_cv = Condition(self.lock)

    def listen(self):
        q = queue.Queue(maxsize=200)
        self.listener = q
        print(self.listener)
        return q
    
    def get(self):
        print("getting")
        print("im in")
        if self.listener is None:
            msg = ""
        else:
            self.lock.acquire()
            print("gonna get")
            print(self.listener.qsize())
            while self.listener.empty():
                print("gonna wait until notified")
                self.empty_cv.wait()
            msg = self.listener.get()
            self.close_cv.notify_all()
            self.lock.release()
        print(msg)
        return msg

    def announce(self, msg):
        print("ANNOUNCING")
        print("IM IN")
        if self.listener is not None:
            self.lock.acquire()
            self.listener.put_nowait(msg)
            self.empty_cv.notify_all()
            self.lock.release()

    
    def close(self):
        # call function, send summary to mongo db
        if self.listener is not None:
            self.lock.acquire()
            while not self.listener.empty():
                self.close_cv.wait()
            self.user = None
            self.listener = None
            self.lock.release()
    
    def isOpen(self):
        return self.listener is not None