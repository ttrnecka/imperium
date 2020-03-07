class NotificationRegister:
    lookup_dict = {}

    @classmethod
    def register(cls,notificator):
        cls.lookup_dict[notificator.descriptor] = notificator

    @classmethod
    def lookup(cls,descriptor):
        return cls.lookup_dict.get(descriptor, None)

class Notificator:
    """Notificator class to send notification to multiple service"""

    def __new__(cls, descriptor, *args, **kwargs):
      notifier = NotificationRegister.lookup(descriptor)
      if not notifier:
        notifier = super(Notificator, cls).__new__(cls, *args, **kwargs)
      return notifier

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