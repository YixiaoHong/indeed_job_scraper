from threading import Thread
from time import sleep

def threaded_function(count,thread_num):
    for i in range(count):
        print("running"+str(thread_num))
        sleep(1)


if __name__ == "__main__":
    thread1 = Thread(target = threaded_function, args = (10,1))
    thread2 = Thread(target=threaded_function, args=(10, 2))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    print("thread finished...exiting")