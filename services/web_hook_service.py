"""WebHook helpers """
import time
import requests

class WebHook:
    """Webhook service namespace"""
    def __init__(self, webhook):
        self.webhook = webhook

    def send(self, msg):
        """Sends `msg` to webhook, returns the response"""
        status_code = 429
        retries = 0
        # 429 means rate limited
        while status_code == 429 and retries < 10:
            req = requests.post(self.webhook, json={'content': msg})
            status_code = req.status_code
            # rate limited
            if status_code == 429:
                wait_for_ms = int(req.json()['retry_after'])
                time.sleep(wait_for_ms/1000)
                retries += 1
        return req
