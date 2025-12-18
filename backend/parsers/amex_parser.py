import re
from .base_parser import BaseParser

class AmexParser(BaseParser):
    def parse(self):
        lines = self.text.split('\n')
        transactions = []
        
        # Regex for "11/03/2023"
        date_pattern_1 = re.compile(r'\d{2}/\d{2}/\d{4}')
        # Regex for "February 14"
        date_pattern_2 = re.compile(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}', re.IGNORECASE)
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            match = date_pattern_1.match(line)
            if not match:
                match = date_pattern_2.match(line)
                
            if match:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        date = " ".join(parts[0:2]) if date_pattern_2.match(line) else parts[0]
                        start_idx = 2 if date_pattern_2.match(line) else 1
                        
                        # Amount logic (from end)
                        amount_idx = -1
                        clean_last = parts[-1].replace(',', '').replace('Rs', '').replace('$','').replace('Cr','').replace('Dr','')
                        if not re.match(r'^-?\d+(\.\d+)?$', clean_last):
                            if len(parts) > start_idx + 1:
                                amount_idx = -2
                        
                        amount_val = float(parts[amount_idx].replace(',', '').replace('Rs', '').replace('$','').replace('Cr','').replace('Dr',''))
                        description = " ".join(parts[start_idx:amount_idx])
                        
                        type = 'debit'
                        # Look at this line and the NEXT line for 'CR'
                        combined_text = line
                        if i + 1 < len(lines):
                            combined_text += " " + lines[i+1]
                            
                        if 'cr' in combined_text.lower() or 'payment' in description.lower() or amount_val < 0:
                            type = 'credit'
                            amount_val = abs(amount_val)
                                
                        transactions.append({
                            "date": date,
                            "ref_no": "N/A",
                            "description": description,
                            "amount": amount_val,
                            "type": type
                        })
                    except Exception:
                        continue

        return {
            "status": "success",
            "issuer": "amex",
            "transactions": transactions,
            "metadata": {}
        }
