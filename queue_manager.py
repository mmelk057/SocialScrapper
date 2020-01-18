from typing import List
from typing import Dict
from threading import Lock
from threading import Thread


class QueueManager:

    def __init__(self, baseUrl: str):
        # By default, we want the first path we search to be already deemed as
        # 'Already Searched'. This is our basePath; aka, the initial user input
        self.alreadySearchedPaths = [baseUrl]
        self.writeLock = Lock()

    def addToSearch(self, urlPath: str, scrapeFunc):
        # Acquire lock
        self.writeLock.acquire(blocking=True)
        if (urlPath not in self.alreadySearchedPaths):
            self.alreadySearchedPaths.append(urlPath)
            currThread = Thread(
                target=scrapeFunc,
                args=(urlPath,))
            # Begin thread scrapping execution
            currThread.start()
        # Release lock
        self.writeLock.release()
