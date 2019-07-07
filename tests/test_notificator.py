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

    return MockResponse("", 204)

def mocked_notifier(msg):
    pass

class TestNotificationRegister(unittest.TestCase):

    def test_has_register(self):
        self.assertDictContainsSubset({},services.NotificationRegister.lookup_dict)

    def test_lookup_notifiers(self):
        notificator = services.Notificator("bank")
        self.assertEqual(services.NotificationRegister.lookup('bank'),notificator, "Notificator is added to register")

        self.assertEqual(services.NotificationRegister.lookup('test'),None, "Looking up non existing notifier")

class TestNotificator(unittest.TestCase):

    def test_notificator_initiation(self):
        notificator = services.Notificator("bank")
        self.assertEqual(notificator.descriptor, "bank", "Notificator has bank descriptor")
        self.assertEqual(notificator.notificators, [], "Notificator has empty list of notificators")
        self.assertEqual(services.NotificationRegister.lookup("bank"),notificator,"Notificator register itself in the notification register")

    def test_notificator_registration(self):
        notificator = services.Notificator("bank")
        notificator.register_notifier(mocked_notifier)
        self.assertEqual(notificator.notificators, [mocked_notifier], "Notificator list of notificators now contains mocked_notifier")

    def test_notify(self):
        noti = mock.MagicMock()
        notificator = services.Notificator("bank")
        notificator.register_notifier(noti)
        notificator.notify("message_sent")
        noti.assert_called_once_with("message_sent")

        # register it agains so it should be called twice
        notificator.register_notifier(noti)
        notificator.notify("2nd_message_sent")
        calls = [mock.call("2nd_message_sent"), mock.call("2nd_message_sent")]
        noti.assert_has_calls(calls)

if __name__ == '__main__':
    unittest.main()