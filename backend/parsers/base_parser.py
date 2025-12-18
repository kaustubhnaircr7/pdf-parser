from abc import ABC, abstractmethod

class BaseParser(ABC):
    def __init__(self, text):
        self.text = text

    @abstractmethod
    def parse(self):
        """
        Parses the text and returns a dictionary of transaction data.
        Expected return format:
        {
            "status": "success",
            "issuer": "issuer_name",
            "transactions": [
                {
                    "date": "YYYY-MM-DD",
                    "description": "Transaction details",
                    "amount": 100.0,
                    "type": "debit/credit"
                },
                ...
            ],
            "metadata": {
                "customer_name": "...",
                "account_number": "...",
                "statement_period": "..."
            }
        }
        """
        pass
