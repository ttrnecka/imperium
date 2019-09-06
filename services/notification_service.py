class NotificationRegister:
    lookup_dict = {}

    @classmethod
    def register(cls,notificator):
        cls.lookup_dict[notificator.descriptor] = notificator

    @classmethod
    def lookup(cls,descriptor):
        return cls.lookup_dict.get(descriptor)

class Notificator:
    """Notificator class to send notification to multiple service"""

    def __init__(self,descriptor):
        self.descriptor = descriptor
        self.notificators = []
        NotificationRegister.register(self)

    def register_notifier(self, func):
        """register notifications function, the function needs to accept one string parameter"""
        self.notificators.append(func)

    def notify(self, msg):
        """calls defined notificator `func` with the message"""
        for notificator in self.notificators:
            notificator(msg)

NotificationService = Notificator("bank")
LedgerNotificationService = Notificator("ledger")
AchievementNotificationService = Notificator("achievement")
AdminNotificationService = Notificator("admin")
TournamentNotificationService = Notificator("tournament")