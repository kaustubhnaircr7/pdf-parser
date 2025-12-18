import re
from .base_parser import BaseParser

class HDFCParser(BaseParser):
    def parse(self):
        lines = self.text.split('\n')
        transactions = []
        
        # HDFC Format: DD/MM/YYYY Description Amount
        # Example: 13/09/2023 Something 100.00
        date_pattern = re.compile(r'\d{2}/\d{2}/\d{4}')
        
        for line in lines:
            try:
                # Basic line filtering
                if not line.strip():
                    continue
                    
                match = date_pattern.match(line.strip())
                if match:
                    parts = line.strip().split()
                    if len(parts) > 3:
                        date = parts[0]
                        
                        # Amount is usually at the end. CR indicates credit
                        type = 'debit'
                        amount_idx = -1
                        
                        if parts[-1].lower() == 'cr':
                            type = 'credit'
                            amount_idx = -2
                        elif 'cr' in parts[-1].lower():
                            type = 'credit'
                        
                        amount_str = parts[amount_idx].replace(',', '').lower().replace('cr', '')
                        
                        # Try to parse amount
                        if re.match(r'^\d+(\.\d+)?$', amount_str):
                            amount = float(amount_str)
                            description = " ".join(parts[1:amount_idx])
                            
                            # Simple HDFC Ref# extractor from description
                            ref_no = "N/A"
                            ref_match = re.search(r'Ref#\s*([\w\d]+)', description)
                            if ref_match:
                                ref_no = ref_match.group(1)
                            
                            transactions.append({
                                "date": date,
                                "ref_no": ref_no,
                                "description": description,
                                "amount": amount,
                                "type": type
                            })
            except Exception:
                continue

        return {
            "status": "success",
            "issuer": "hdfc",
            "transactions": transactions,
            "metadata": {}
        }
