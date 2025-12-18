import re
from .base_parser import BaseParser

class WellsFargoParser(BaseParser):
    def deduplicate(self, text):
        if not text:
            return text
        result = []
        i = 0
        # Simple character doubling detection
        while i < len(text):
            char = text[i]
            result.append(char)
            if i + 1 < len(text) and text[i+1] == char and char != ' ' and char != '\n':
                i += 2
            else:
                i += 1
        return "".join(result)

    def parse(self):
        # Clean the text from doubling artifacts
        clean_text = self.deduplicate(self.text)
        lines = clean_text.split('\n')
        transactions = []
        
        # Patterns
        # Date: MM/DD at start (allowing for some leading artifacts)
        date_pattern = re.compile(r'(\d{2}/\d{2}(?:/\d{4})?)')
        # Amount: decimal with optional minus at end of part - FIXED to allow 1 or 2 decimals
        amount_pattern = re.compile(r'(-?[\d,]+\.\d{1,2})')
        
        dates_only = []
        entries_only = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip header info and summary fields unless they have a date
            if any(x in line.upper() for x in ["SUMMARY", "BALANCE", "PAYMENT DUE", "CREDIT LIMIT", "MINIMUM PAYMENT"]):
                 if not re.search(r'\d{2}/\d{2} ', line):
                    continue

            parts = line.split()
            if not parts: continue
            
            # Check for date anywhere in the first few parts (e.g. Transaction Date vs Post Date)
            date_str = None
            date_idx = -1
            for i in range(min(3, len(parts))): # Checked first 3 parts
                if date_pattern.fullmatch(parts[i]):
                    date_str = parts[i]
                    date_idx = i
                    break
            
            # Check if last part is amount
            last_part = parts[-1].replace('$', '').replace(',', '')
            amt_match = amount_pattern.fullmatch(last_part)
            
            if date_str and amt_match:
                # Direct Hit
                amt_val = float(amt_match.group(1))
                
                # Description is middle parts
                # Skip duplicate date if present (e.g. 08/23 08/23 Description ...)
                start_desc = date_idx + 1
                while start_desc < len(parts) and date_pattern.fullmatch(parts[start_desc]):
                    start_desc += 1
                    
                desc = " ".join(parts[start_desc:-1]).strip()
                if not desc:
                    desc = "Transaction"
                
                transactions.append({
                    "date": date_str,
                    "ref_no": "N/A",
                    "description": desc,
                    "amount": abs(amt_val),
                    "type": 'credit' if amt_val < 0 else 'debit'
                })
            elif date_str and len(parts) == 1:
                # Columnar Date
                dates_only.append(date_str)
            elif amt_match:
                # Columnar Amount
                amt_val = float(amt_match.group(1))
                desc = " ".join(parts[:-1]).strip()
                entries_only.append({
                    "amount": abs(amt_val),
                    "type": 'credit' if amt_val < 0 else 'debit',
                    "description": desc
                })

        # Fallback: if no direct hits but we have columnar data
        if not transactions and dates_only and entries_only:
            count = min(len(dates_only), len(entries_only))
            for i in range(count):
                transactions.append({
                    "date": dates_only[i],
                    "ref_no": "N/A",
                    "description": entries_only[i]['description'],
                    "amount": entries_only[i]['amount'],
                    "type": entries_only[i]['type']
                })
        
        return {
            "status": "success",
            "issuer": "wellsfargo",
            "transactions": transactions,
            "metadata": {
                "note": f"Extracted {len(transactions)} transactions."
            }
        }
