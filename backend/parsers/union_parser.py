import re
from .base_parser import BaseParser

class UnionParser(BaseParser):
    def parse(self):
        lines = self.text.split('\n')
        transactions = []
        
        # US Bank / Union format often MM/DD/YY or MM/DD
        # Relaxed regex to allow MM/DD (year optional)
        date_pattern = re.compile(r'\d{2}/\d{2}(/\d{2,4})?')
        
        # Since the sample is likely empty/summary only, this is a best-effort parser
        # for standard statement lines.
        
        ignored_zero_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            match = date_pattern.match(line)
            if match:
                parts = line.split()
                if len(parts) > 3:
                     # Attempt to find amount at end
                    try:
                        amount_str = parts[-1].replace('$', '').replace(',', '')
                        description = " ".join(parts[1:-1])
                        
                        # Check if amount is valid
                        if re.match(r'^-?[\d,]+(\.\d+)?$', amount_str):
                            amount = float(amount_str)
                            
                            # Optional: Skip exactly 0.00 amounts to avoid cluttering with summary lines
                            if abs(amount) < 0.01:
                                ignored_zero_count += 1
                                continue
                                
                            transactions.append({
                                "date": parts[0],
                                "ref_no": "N/A",
                                "description": description,
                                "amount": abs(amount),
                                "type": 'credit' if amount < 0 else 'debit'
                            })
                    except Exception:
                        pass
                        
        note = "Union parser active."
        if not transactions:
            if ignored_zero_count > 0:
                note += f" No actionable transactions found, but skipped {ignored_zero_count} zero-value summary entries (e.g. $0.00 Fees/Interest)."
            else:
                note += " No transactions found. Statement appears to be summary-only."
        
        return {
            "status": "success",
            "issuer": "union",
            "transactions": transactions,
            "metadata": {"note": note}
        }
