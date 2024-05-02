from threading import Thread
import time
from test2 import stuff

mylist = []
thread = Thread(target=stuff, args=("T1", mylist))
thread.daemon = True
thread.start()
time.sleep(2)
print(mylist)