import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Database Initialization
def init_database():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    
    # Create expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date DATE NOT NULL
        )
    ''')
    
    # Create budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            budget_amount REAL NOT NULL
        )
    ''')

    # Create a total budget table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS total_budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            budget_amount REAL NOT NULL
        )
    ''')
    
    conn.commit()
    return conn, cursor

# Add Expense
def add_expense(conn, cursor, amount, category, description, date):
    cursor.execute('''
        INSERT INTO expenses (amount, category, description, date) 
        VALUES (?, ?, ?, ?)
    ''', (amount, category, description, date))
    conn.commit()

# Set Budget for Category
def set_budget(conn, cursor, category, budget_amount):
    cursor.execute('''
        INSERT OR REPLACE INTO budgets (category, budget_amount) 
        VALUES (?, ?)
    ''', (category, budget_amount))
    conn.commit()

# Set Total Budget
def set_total_budget(conn, cursor, budget_amount):
    cursor.execute('''
        DELETE FROM total_budget
    ''')
    cursor.execute('''
        INSERT INTO total_budget (budget_amount) 
        VALUES (?)
    ''', (budget_amount,))
    conn.commit()

# Get Total Budget
def get_total_budget(cursor):
    cursor.execute('SELECT budget_amount FROM total_budget LIMIT 1')
    result = cursor.fetchone()
    return result[0] if result else 0

# Get Total Expenses
def get_total_expenses(cursor):
    cursor.execute('SELECT SUM(amount) FROM expenses')
    return cursor.fetchone()[0] or 0

# Get Expenses by Category
def get_expenses_by_category(cursor):
    cursor.execute('''
        SELECT category, SUM(amount) as total_amount 
        FROM expenses 
        GROUP BY category
    ''')
    return dict(cursor.fetchall())

# Get Budget for Category
def get_budget(cursor, category):
    cursor.execute('SELECT budget_amount FROM budgets WHERE category = ?', (category,))
    result = cursor.fetchone()
    return result[0] if result else 0

# Delete Expense
def delete_expense(conn, cursor, expense_id):
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()

# Delete Budget
def delete_budget(conn, cursor, category):
    cursor.execute('DELETE FROM budgets WHERE category = ?', (category,))
    conn.commit()

# Main Streamlit App
def main():
    st.title("💰 Expense Tracker")
    
    # Initialize database
    conn, cursor = init_database()
    
    # Sidebar Navigation
    menu = ["Add Expense", "Expense Report", "Budget Management", "Visualizations"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    # Add Expense Section
    if choice == "Add Expense":
        st.subheader("Add New Expense")
        
        # Predefined expense categories
        categories = [
            "Food", "Transportation", "Utilities", "Entertainment", 
            "Shopping", "Healthcare", "Education", "Rent", "Miscellaneous"
        ]
        
        # Expense input form
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Expense Amount (₹)", min_value=0.0, step=10.0)
        
        with col2:
            category = st.selectbox("Expense Category", categories)
        
        description = st.text_input("Description (Optional)")
        expense_date = st.date_input("Expense Date", datetime.now())
        
        if st.button("Add Expense"):
            if amount > 0:
                add_expense(conn, cursor, amount, category, description, expense_date)
                st.success("Expense Added Successfully!")
            else:
                st.error("Please enter a valid amount")
    
    # Expense Report Section
    elif choice == "Expense Report":
        st.subheader("Expense Report")
        
        # Get expenses
        cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
        expenses_df = pd.DataFrame(cursor.fetchall(), 
                                   columns=['ID', 'Amount', 'Category', 'Description', 'Date'])
        
        # Display total expenses
        total_expenses = get_total_expenses(cursor)
        st.metric("Total Expenses", f"₹{total_expenses:.2f}")
        
        # Expense table with delete button
        if not expenses_df.empty:
            for _, row in expenses_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 4, 1])
                col1.text(row['ID'])
                col2.text(row['Category'])
                col3.text(f"₹{row['Amount']:.2f}")
                col4.text(row['Description'])
                if col5.button("Delete", key=row['ID']):
                    delete_expense(conn, cursor, row['ID'])
                    st.experimental_rerun()
        else:
            st.info("No expenses found.")
    
    # Budget Management Section
    elif choice == "Budget Management":
        st.subheader("Budget Management")
        
        # Set total budget
        st.write("### Set Total Budget")
        total_budget = st.number_input("Total Budget (₹)", min_value=0.0, step=100.0)
        if st.button("Set Total Budget"):
            set_total_budget(conn, cursor, total_budget)
            st.success("Total Budget Set Successfully!")
        
        st.write("### Set Category-wise Budget")
        categories = [
            "Food", "Transportation", "Utilities", "Entertainment", 
            "Shopping", "Healthcare", "Education", "Rent", "Miscellaneous"
        ]
        
        category = st.selectbox("Select Category", categories)
        budget_amount = st.number_input("Set Budget Amount (₹)", min_value=0.0, step=100.0)
        
        if st.button("Set Category Budget"):
            set_budget(conn, cursor, category, budget_amount)
            st.success("Category Budget Set Successfully!")
        
        # Display current budgets
        st.write("### Current Budgets")
        cursor.execute('SELECT * FROM budgets')
        budgets_df = pd.DataFrame(cursor.fetchall(), columns=['Category', 'Budget'])
        if not budgets_df.empty:
            for _, row in budgets_df.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.text(row['Category'])
                col2.text(f"₹{row['Budget']:.2f}")
                if col3.button("Delete", key=row['Category']):
                    delete_budget(conn, cursor, row['Category'])
                    st.experimental_rerun()
        else:
            st.info("No budgets found.")

        # Display total budget
        st.write("### Total Budget")
        total_budget = get_total_budget(cursor)
        st.metric("Total Budget", f"₹{total_budget:.2f}")
    
    # Visualizations Section
    elif choice == "Visualizations":
        st.subheader("Expense Visualizations")
        
        # Pie Chart of Expenses by Category
        expenses_by_category = get_expenses_by_category(cursor)
        
        if expenses_by_category:
            fig1, ax1 = plt.subplots()
            ax1.pie(expenses_by_category.values(), 
                    labels=expenses_by_category.keys(), 
                    autopct='%1.1f%%')
            ax1.set_title('Expenses by Category')
            st.pyplot(fig1)
        
        # Bar Chart of Budget vs Actual Spending
        st.write("### Budget vs Actual Spending")
        categories = list(expenses_by_category.keys())
        actual_spending = list(expenses_by_category.values())
        budgets = [get_budget(cursor, cat) for cat in categories]
        
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        x = range(len(categories))
        width = 0.35
        
        ax2.bar([i - width/2 for i in x], budgets, width, label='Budget', color='green')
        ax2.bar([i + width/2 for i in x], actual_spending, width, label='Actual Spending', color='red')
        
        ax2.set_xlabel('Categories')
        ax2.set_ylabel('Amount (₹)')
        ax2.set_title('Budget vs Actual Spending')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45)
        ax2.legend()
        
        st.pyplot(fig2)
    
    # Close database connection
    conn.close()

if __name__ == "__main__":
    main()
