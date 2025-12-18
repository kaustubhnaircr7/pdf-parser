import re
from .base_parser import BaseParser

class ICICIParser(BaseParser):
    def parse(self):
        lines = self.text.split('\n')
        transactions = []
        
        # Regex for ICICI date format (DD/MM/YYYY)
        # Adjust based on actual PDF content inspection if needed
        date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
        
        for line in lines:
            # Placeholder logic - this needs to be refined based on actual PDF structure
            # Looking for lines that start with a date
            match = date_pattern.match(line.strip())
            if match:
                parts = line.split()
                if len(parts) > 3:
                    try:
                        date = parts[0]
                        ref_no = parts[1] if parts[1].isdigit() else "N/A"
                        
                        # Detect credit indicator at the end
                        type = 'debit'
                        amount_idx = -1
                        
                        if parts[-1].lower() == 'cr':
                            type = 'credit'
                            amount_idx = -2
                        elif 'cr' in parts[-1].lower():
                            type = 'credit'
                        
                        amount_str = parts[amount_idx].replace(',', '').lower().replace('cr', '')
                        amount = float(amount_str)
                            
                        # If we found a ref_no, description starts at 2, otherwise 1
                        desc_start = 2 if ref_no != "N/A" else 1
                        description = " ".join(parts[desc_start:amount_idx])
                        
                        transactions.append({
                            "date": date,
                            "ref_no": ref_no,
                            "description": description,
                            "amount": amount,
                            "type": type
                        })
                    except (ValueError, IndexError):
                        continue

        return {
            "status": "success",
            "issuer": "icici",
            "transactions": transactions,
            "metadata": {}
        }
