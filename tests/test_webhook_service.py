import requests
import unittest
from unittest import mock
import services

def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://webhook_ok':
        return MockResponse("", 204)
    elif args[0] == 'http://webhook_retry':
        return MockResponse({"retry_after": 5}, 429)
    elif args[0] == 'http://webhook_failure':
        return MockResponse(None, 404)

    return MockResponse(None, 404)

class TestWebhookService(unittest.TestCase):

    def test_webhook_initiation(self):
        wb = services.WebHook("webhook")
        self.assertIs(wb.webhook, "webhook", "Webhook instance should have attribute webhook")

    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_webhook_ok_send(self, mock_post):
        wb = services.WebHook("http://webhook_ok")
        req = wb.send("message")
        self.assertEqual(req.status_code,204)
        self.assertIn(mock.call('http://webhook_ok', json={'content': 'message'}), mock_post.call_args_list)

    # when discord sends 429 it is rate limiting and it will return with retry_after parameter
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_webhook_retry_send(self, mock_post):
        wb = services.WebHook("http://webhook_retry")
        req = wb.send("message")
        self.assertEqual(req.status_code,429)
        self.assertIn(mock.call('http://webhook_retry', json={'content': 'message'}), mock_post.call_args_list)
        self.assertEqual(len(mock_post.call_args_list), 10)

    # returns once if not 204 or 429
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_webhook_failure_send(self, mock_post):
        wb = services.WebHook("http://webhook_failure")
        req = wb.send("message")
        self.assertEqual(req.status_code,404)
        self.assertIn(mock.call('http://webhook_failure', json={'content': 'message'}), mock_post.call_args_list)
        self.assertEqual(len(mock_post.call_args_list), 1)

if __name__ == '__main__':
    unittest.main()