import re

def detect_issuer(text):
    """
    Analyzes the text to detect the credit card issuer/bank.
    Returns the issuer name as a lowercase string.
    """
    if not text:
        return None
        
    text_lower = text.lower()
    
    # ICICI
    if 'icici bank' in text_lower or 'icicibank' in text_lower:
        return 'icici'
    
    # HDFC
    elif 'hdfc bank' in text_lower or 'hdfcbank' in text_lower:
        return 'hdfc'
    
    # SBI
    elif 'sbi card' in text_lower or 'sbicard' in text_lower:
        return 'sbi'
    
    # Axis
    elif 'axis bank' in text_lower or 'axisbank' in text_lower:
        return 'axis'
    
    # Amex
    elif 'american express' in text_lower or 'amex' in text_lower or 'membership number' in text_lower:
        return 'amex'
        
    # Chase
    elif 'chase credit card' in text_lower or 'chase.com' in text_lower:
        return 'chase'
        
    # Wells Fargo
    elif 'wells fargo' in text_lower:
        return 'wellsfargo'
        
    # Union Bank / US Bank (The sample 'union.pdf' seems to be US Bank 'USB')
    elif 'union bank' in text_lower or 'usb cc' in text_lower or 'us bank' in text_lower:
        return 'union'
        
    return None
