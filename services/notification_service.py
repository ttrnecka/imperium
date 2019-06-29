"""Notification services"""
class NotificationService:
    """Basic Notification service used for bank notifications"""
    notificators = []

    @classmethod
    def notify(cls, msg):
        """calls defined notificator `func` with the message"""
        for notificator in cls.notificators:
            notificator(msg)

    @classmethod
    def register_notifier(cls, func):
        """register notifications function, the function needs to accept one string parameter"""
        cls.notificators.append(func)

class LedgerNotificationService:
    """Basic Notification service used for ledger notifications"""
    notificators = []

    @classmethod
    def notify(cls, msg):
        """calls defined notificator `func` with the message"""
        for notificator in cls.notificators:
            notificator(msg)

    @classmethod
    def register_notifier(cls, func):
        """register notifications function, the function needs to accept one string parameter"""
        cls.notificators.append(func)

class AchievementNotificationService:
    """Basic Notification service used for achievement notifications"""
    notificators = []

    @classmethod
    def notify(cls, msg):
        """calls defined notificator `func` with the message"""
        for notificator in cls.notificators:
            notificator(msg)

    @classmethod
    def register_notifier(cls, func):
        """register notifications function, the function needs to accept one string parameter"""
        cls.notificators.append(func)
