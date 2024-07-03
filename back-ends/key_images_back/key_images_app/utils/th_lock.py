import os
import time
from threading import Thread

class th_lock:

    # true if loading has finished
    loading_finished = False
    # thread used to wait
    map_loading_thread = None

    # thread function
    def is_data_ready(self):
        while True:
            if self.loading_finished:
                return
            time.sleep(0.1)

    # wait for thread to finish
    def wait(self):
        if self.map_loading_thread:
            self.map_loading_thread.join()

    # Creates thread
    def start_loading(self):
        self.loading_finished = False
        self.map_loading_thread = Thread(target=self.is_data_ready)
        self.map_loading_thread.start()
    
    # Makes thread to finish
    def end_loading(self):
        self.loading_finished = True
