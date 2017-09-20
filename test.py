import threading
import time
 
def worker():
    print(123)
    time.sleep(1)
    return
 
for i in range(5):
    t = threading.Thread(target=worker)
    t.start()