"""
Initialize FinSpeak database with schema and mock data
Run this once to set up the database
"""
import sqlite3
from db import DB_PATH

def init_database():
    """Initialize database with schema and mock data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔧 Creating database schema...")
    
    # ========================================================================
    # CREATE TABLES
    # ========================================================================
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            account_number TEXT NOT NULL,
            balance INTEGER NOT NULL,
            bank TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beneficiaries (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            account_number TEXT NOT NULL,
            bank TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id TEXT NOT NULL,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL,
            balance_after INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(id)
        )
    """)
    
    # ========================================================================
    # INSERT MOCK DATA (only if tables are empty)
    # ========================================================================
    
    cursor.execute("SELECT COUNT(*) FROM accounts")
    if cursor.fetchone()[0] == 0:
        print("📊 Inserting mock data...")
        
        # Insert accounts
        accounts = [
            ("acc_savings_primary", "demo_user", "Primary Savings", "savings", "XXXX7890", 1000000, "Grace Hopper Bank"),
            ("acc_savings_emergency", "demo_user", "Emergency Fund", "savings", "XXXX3456", 2000000, "Grace Hopper Bank"),
            ("acc_current", "demo_user", "Current Account", "current", "XXXX1234", 500000, "Grace Hopper Bank"),
        ]
        cursor.executemany(
            "INSERT INTO accounts (id, user_id, name, type, account_number, balance, bank) VALUES (?, ?, ?, ?, ?, ?, ?)",
            accounts
        )
        print(f"  ✅ Inserted {len(accounts)} accounts")
        
        # Insert beneficiaries
        beneficiaries = [
            ("ben_pratap_kumar", "demo_user", "Pratap Kumar", "XXXX1234", "HDFC Bank"),
            ("ben_pratap_singh", "demo_user", "Pratap Singh", "XXXX5678", "Grace Hopper Bank"),
            ("ben_raj_sharma", "demo_user", "Raj Sharma", "XXXX9012", "SBI"),
        ]
        cursor.executemany(
            "INSERT INTO beneficiaries (id, user_id, name, account_number, bank) VALUES (?, ?, ?, ?, ?)",
            beneficiaries
        )
        print(f"  ✅ Inserted {len(beneficiaries)} beneficiaries")
        
        # Insert transactions for Primary Savings (last 3 months from Nov 22, 2025)
        transactions_primary = [
            # November 2025 (recent - this week)
            ("acc_savings_primary", "2025-11-30", "debit", "Netflix Subscription", 650, 1000000),
            ("acc_savings_primary", "2025-11-29", "debit", "Zomato Order", 580, 1000650),
            ("acc_savings_primary", "2025-11-28", "credit", "Cashback", 150, 1001230),
            ("acc_savings_primary", "2025-11-27", "debit", "Uber Ride", 320, 1001080),
            ("acc_savings_primary", "2025-11-26", "debit", "Pharmacy", 420, 1001400),
            ("acc_savings_primary", "2025-11-25", "debit", "Grocery Store", 1350, 1001820),
            ("acc_savings_primary", "2025-11-24", "debit", "Coffee Shop", 180, 1003170),
            ("acc_savings_primary", "2025-11-23", "debit", "Book Purchase", 750, 1003350),
            ("acc_savings_primary", "2025-11-22", "debit", "Amazon Purchase", 1200, 1004100),
            ("acc_savings_primary", "2025-11-21", "debit", "Swiggy Order", 450, 1005300),
            ("acc_savings_primary", "2025-11-20", "debit", "Uber Ride", 280, 1000450),
            ("acc_savings_primary", "2025-11-19", "credit", "Refund", 1200, 1000730),
            ("acc_savings_primary", "2025-11-18", "debit", "Amazon Purchase", 1500, 999530),
            ("acc_savings_primary", "2025-11-17", "debit", "Coffee Shop", 150, 1001030),
            ("acc_savings_primary", "2025-11-16", "debit", "Grocery Store", 1200, 1001180),
            ("acc_savings_primary", "2025-11-15", "credit", "Salary Credit", 50000, 1002380),
            ("acc_savings_primary", "2025-11-14", "debit", "Electricity Bill", 850, 952380),
            ("acc_savings_primary", "2025-11-12", "debit", "Online Shopping", 2500, 953230),
            ("acc_savings_primary", "2025-11-10", "debit", "ATM Withdrawal", 5000, 955730),
            ("acc_savings_primary", "2025-11-08", "credit", "Transfer from Raj Sharma", 2000, 960730),
            ("acc_savings_primary", "2025-11-05", "debit", "Restaurant", 750, 958730),
            ("acc_savings_primary", "2025-11-03", "debit", "Medical Store", 850, 959480),
            ("acc_savings_primary", "2025-11-01", "credit", "Interest Credit", 250, 960330),
            # October 2025 (last month)
            ("acc_savings_primary", "2025-10-28", "debit", "Movie Tickets", 600, 960080),
            ("acc_savings_primary", "2025-10-25", "debit", "Petrol", 1500, 960680),
            ("acc_savings_primary", "2025-10-22", "debit", "Book Purchase", 800, 962180),
            ("acc_savings_primary", "2025-10-20", "credit", "Cashback", 300, 962980),
            ("acc_savings_primary", "2025-10-18", "debit", "Mobile Recharge", 500, 962680),
            ("acc_savings_primary", "2025-10-15", "credit", "Salary Credit", 50000, 963180),
            ("acc_savings_primary", "2025-10-12", "debit", "Insurance Premium", 5000, 913180),
            ("acc_savings_primary", "2025-10-08", "debit", "Pharmacy", 450, 918180),
            ("acc_savings_primary", "2025-10-05", "debit", "ATM Withdrawal", 3000, 918630),
            ("acc_savings_primary", "2025-10-01", "credit", "Interest Credit", 240, 921630),
            # September 2025 (2 months ago)
            ("acc_savings_primary", "2025-09-28", "debit", "Gift Purchase", 3000, 921390),
            ("acc_savings_primary", "2025-09-25", "debit", "Uber Ride", 280, 924390),
            ("acc_savings_primary", "2025-09-20", "credit", "Freelance Payment", 10000, 924670),
            ("acc_savings_primary", "2025-09-15", "credit", "Salary Credit", 50000, 914670),
            ("acc_savings_primary", "2025-09-10", "debit", "Electricity Bill", 920, 864670),
            ("acc_savings_primary", "2025-09-05", "debit", "ATM Withdrawal", 4000, 865590),
            ("acc_savings_primary", "2025-09-01", "credit", "Interest Credit", 230, 869590),
            # August 2025 (3 months ago)
            ("acc_savings_primary", "2025-08-28", "debit", "Restaurant", 750, 869360),
            ("acc_savings_primary", "2025-08-25", "debit", "Shopping", 2500, 870110),
            ("acc_savings_primary", "2025-08-22", "credit", "Refund", 1200, 872610),
        ]
        
        # Insert transactions for Emergency Fund (last 3 months from Nov 22, 2025)
        transactions_emergency = [
            ("acc_savings_emergency", "2025-11-28", "credit", "Interest Credit", 480, 2000000),
            ("acc_savings_emergency", "2025-11-25", "debit", "Medical Emergency", 15000, 1999520),
            ("acc_savings_emergency", "2025-11-20", "debit", "Home Repair", 8500, 2014520),
            ("acc_savings_emergency", "2025-11-15", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 2023020),
            ("acc_savings_emergency", "2025-11-10", "debit", "Car Repair", 12000, 2003020),
            ("acc_savings_emergency", "2025-11-01", "credit", "Interest Credit", 450, 2015020),
            ("acc_savings_emergency", "2025-10-22", "debit", "Emergency Travel", 18000, 2014570),
            ("acc_savings_emergency", "2025-10-15", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 2032570),
            ("acc_savings_emergency", "2025-10-08", "debit", "Urgent Expense", 5000, 2012570),
            ("acc_savings_emergency", "2025-10-01", "credit", "Interest Credit", 420, 2017570),
            ("acc_savings_emergency", "2025-09-18", "debit", "Medical Bills", 9500, 2017150),
            ("acc_savings_emergency", "2025-09-15", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 2026650),
            ("acc_savings_emergency", "2025-09-01", "credit", "Interest Credit", 410, 2006650),
            ("acc_savings_emergency", "2025-08-25", "debit", "Emergency Fund Withdrawal", 7000, 2006240),
            ("acc_savings_emergency", "2025-08-22", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 2013240),
        ]
        
        # Insert transactions for Current Account (last 3 months from Nov 22, 2025)
        transactions_current = [
            # November 2025 (recent - this week)
            ("acc_current", "2025-11-30", "debit", "Restaurant", 950, 500000),
            ("acc_current", "2025-11-29", "debit", "Fuel", 1600, 500950),
            ("acc_current", "2025-11-28", "debit", "Grocery", 1100, 502550),
            ("acc_current", "2025-11-27", "credit", "Refund", 250, 503650),
            ("acc_current", "2025-11-26", "debit", "Coffee Shop", 200, 503400),
            ("acc_current", "2025-11-25", "debit", "Movie Tickets", 450, 503600),
            ("acc_current", "2025-11-24", "debit", "Pharmacy", 380, 504050),
            ("acc_current", "2025-11-23", "debit", "Uber Ride", 290, 504430),
            ("acc_current", "2025-11-22", "debit", "Shopping", 1800, 504720),
            ("acc_current", "2025-11-21", "debit", "Grocery", 1200, 506520),
            ("acc_current", "2025-11-20", "debit", "Fuel", 1800, 501200),
            ("acc_current", "2025-11-18", "debit", "Coffee Shop", 150, 503000),
            ("acc_current", "2025-11-17", "debit", "Pharmacy", 450, 503150),
            ("acc_current", "2025-11-16", "credit", "Refund", 300, 503600),
            ("acc_current", "2025-11-14", "debit", "Rent Payment", 12000, 503300),
            ("acc_current", "2025-11-11", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 515300),
            ("acc_current", "2025-11-09", "debit", "Gas Station", 600, 495300),
            ("acc_current", "2025-11-06", "debit", "Restaurant", 850, 495900),
            ("acc_current", "2025-11-04", "debit", "Movie Tickets", 400, 496750),
            ("acc_current", "2025-11-02", "debit", "Book Store", 550, 497150),
            # October 2025 (last month)
            ("acc_current", "2025-10-30", "debit", "Utility Bill", 950, 497700),
            ("acc_current", "2025-10-27", "debit", "Shopping", 2500, 498650),
            ("acc_current", "2025-10-23", "credit", "Cashback", 200, 501150),
            ("acc_current", "2025-10-20", "debit", "Cab Fare", 350, 500950),
            ("acc_current", "2025-10-14", "debit", "Rent Payment", 12000, 501300),
            ("acc_current", "2025-10-11", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 513300),
            ("acc_current", "2025-10-08", "debit", "Dinner", 950, 493300),
            ("acc_current", "2025-10-05", "debit", "Grocery", 1200, 494250),
            # September 2025 (2 months ago)
            ("acc_current", "2025-09-28", "debit", "Fuel", 1800, 495450),
            ("acc_current", "2025-09-22", "debit", "Shopping", 2500, 497250),
            ("acc_current", "2025-09-14", "debit", "Rent Payment", 12000, 499750),
            ("acc_current", "2025-09-11", "credit", "Transfer from Savings Account (XXXX7890)", 20000, 511750),
            ("acc_current", "2025-09-08", "debit", "Restaurant", 850, 491750),
            # August 2025 (3 months ago)
            ("acc_current", "2025-08-28", "debit", "Grocery", 1200, 492600),
            ("acc_current", "2025-08-25", "debit", "Movie Tickets", 400, 493800),
            ("acc_current", "2025-08-22", "credit", "Cashback", 200, 494200),
        ]
        
        all_transactions = transactions_primary + transactions_emergency + transactions_current
        cursor.executemany(
            "INSERT INTO transactions (account_id, date, type, description, amount, balance_after) VALUES (?, ?, ?, ?, ?, ?)",
            all_transactions
        )
        print(f"  ✅ Inserted {len(all_transactions)} transactions")
    else:
        print("  ℹ️  Database already contains data, skipping mock data insertion")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database initialized successfully!")
    print(f"📁 Database file: {DB_PATH}")
    print("\n🚀 You can now start the server with: python server.py")

if __name__ == "__main__":
    init_database()
