from datetime import datetime

class Metrics:

    total_requests = 0

    @classmethod
    def request(cls):
        cls.total_requests += 1

    @classmethod
    def stats(cls):

        return {
            "requests": cls.total_requests,
            "time": datetime.now().strftime("%H:%M:%S")
        }