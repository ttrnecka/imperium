"""TransactionService helpers"""
from models.data_models import Transaction
from .notification_service import NotificationService

class TransactionService:
    """Namespace class for Transaction actions"""

    @classmethod
    def process(cls, coach, amount, reason):
        """Process transaction and notifies the coach on discord"""
        transaction = Transaction(description=reason, price=amount)
        coach.make_transaction(transaction)
        msg = f"<@{coach.disc_id}>: Your bank has been updated by **{-1*amount}** coins - {reason}"
        NotificationService.notify(msg)
        return True
