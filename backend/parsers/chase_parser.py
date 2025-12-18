import re
from .base_parser import BaseParser

class ChaseParser(BaseParser):
    def parse(self):
        lines = self.text.split('\n')
        transactions = []
        
        # Chase Format from dump: 04/12 PayPal***1NE1 -137.00
        # MM/DD format
        date_pattern = re.compile(r'\d{2}/\d{2}\s+')
        
        for line in lines:
            line = line.strip()
            match = date_pattern.match(line)
            if match:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        date = parts[0] 
                        # Append current year if missing? Or just keep MM/DD
                        
                        # Chase puts amount slightly differently sometimes
                        # Look for number at end or near end
                        # From dump: -137.00 $13863 (Amount, Balance)
                        # So amount is second to last if balance is present
                        
                        amount_str = parts[-2].replace(',', '')
                        if '$' in parts[-1] and '$' not in amount_str:
                             # Likely the last column is balance, second last is amount
                             pass
                        elif '$' in amount_str:
                            amount_str = amount_str.replace('$', '')
                            
                        if re.match(r'^-?\d+(\.\d+)?$', amount_str):
                            amount = float(amount_str)
                            description = " ".join(parts[1:-2])
                            
                            transactions.append({
                                "date": date,
                                "ref_no": "N/A",
                                "description": description,
                                "amount": abs(amount),
                                "type": 'credit' if amount < 0 else 'debit'
                            })
                    except:
                        continue
                        
        return {
            "status": "success",
            "issuer": "chase",
            "transactions": transactions,
            "metadata": {}
        }
