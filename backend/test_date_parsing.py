"""Test relative date parsing for transaction history"""
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re

def parse_relative_date(date_range: str):
    """Test function to parse relative dates"""
    today = datetime.now()
    date_range_lower = date_range.lower()
    
    if 'week' in date_range_lower:
        match = re.search(r'(\d+)\s*weeks?', date_range_lower)
        weeks = int(match.group(1)) if match else 1
        start_date = (today - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        return start_date, today.strftime('%Y-%m-%d'), f"{weeks} week(s)"
    
    elif 'month' in date_range_lower:
        match = re.search(r'(\d+)\s*months?', date_range_lower)
        months = int(match.group(1)) if match else 1
        start_date = (today - relativedelta(months=months)).strftime('%Y-%m-%d')
        return start_date, today.strftime('%Y-%m-%d'), f"{months} month(s)"
    
    elif 'day' in date_range_lower:
        match = re.search(r'(\d+)\s*days?', date_range_lower)
        days = int(match.group(1)) if match else 7
        start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        return start_date, today.strftime('%Y-%m-%d'), f"{days} day(s)"
    
    return None, None, "Invalid"

# Test cases
test_cases = [
    "last 2 weeks",
    "last 2 week",
    "last week",
    "last 5 days",
    "last 5 day",
    "last day",
    "last 2 months",
    "last 2 month",
    "last month",
    "last 3 months",
    "Last 10 Days",
]

print(f"Current date from datetime.now(): {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Current date (date only): {datetime.now().strftime('%Y-%m-%d')}\n")
print("="*60)
print("Testing relative date parsing:\n")

for test in test_cases:
    start, end, parsed = parse_relative_date(test)
    if start:
        days_diff = (datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days
        print(f"✅ '{test}' → {parsed} ({days_diff} days)")
        print(f"   Range: {start} to {end}\n")
    else:
        print(f"❌ '{test}' → Failed to parse\n")
