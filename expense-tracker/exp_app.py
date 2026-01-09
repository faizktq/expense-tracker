import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Database Initialization
def init_database():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date DATE NOT NULL
        )
    ''')
    
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS budgets (
            category TEXT PRIMARY KEY,
            budget_amount REAL NOT NULL
        )
    ''')
    
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
    cursor.execute('DELETE FROM total_budget')
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

# Export Data to CSV
def export_expenses_to_csv(cursor):
    cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
    expenses_df = pd.DataFrame(cursor.fetchall(), columns=['ID', 'Amount', 'Category', 'Description', 'Date'])
    return expenses_df.to_csv(index=False)

# Main Streamlit App
def main():
    st.title("💰 Expense Tracker")

    conn, cursor = init_database()

    menu = ["Add Expense", "Expense Report", "Budget Management", "Visualizations", "Export Data"]
    choice = st.sidebar.selectbox("Menu", menu)

    # ------------------ ADD EXPENSE ------------------
    if choice == "Add Expense":
        st.subheader("Add New Expense")

        categories = [
            "Food", "Transportation", "Utilities", "Entertainment", 
            "Shopping", "Healthcare", "Education", "Rent", "Miscellaneous"
        ]

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

    # ------------------ EXPENSE REPORT ------------------
    elif choice == "Expense Report":
        st.subheader("Expense Report")

        cursor.execute('SELECT * FROM expenses ORDER BY date DESC')
        expenses_df = pd.DataFrame(cursor.fetchall(), 
                                   columns=['ID', 'Amount', 'Category', 'Description', 'Date'])

        total_expenses = get_total_expenses(cursor)
        st.metric("Total Expenses", f"₹{total_expenses:.2f}")

        st.dataframe(expenses_df)

        if not expenses_df.empty:
            delete_id = st.selectbox(
                "Select Expense ID to Delete",
                options=expenses_df["ID"].tolist()
            )

            if st.button("Delete Selected Expense"):
                delete_expense(conn, cursor, delete_id)
                st.success(f"Expense ID {delete_id} deleted!")
                st.experimental_rerun()
        else:
            st.info("No expenses found.")

    # ------------------ BUDGET MANAGEMENT ------------------
    elif choice == "Budget Management":
        st.subheader("Budget Management")

        st.write("### Set Total Budget")
        total_budget_input = st.number_input("Total Budget (₹)", min_value=0.0, step=100.0)
        if st.button("Set Total Budget"):
            set_total_budget(conn, cursor, total_budget_input)
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

        st.write("### Current Budgets")
        cursor.execute('SELECT * FROM budgets')
        budgets_df = pd.DataFrame(cursor.fetchall(), columns=['Category', 'Budget'])

        st.dataframe(budgets_df)

        if not budgets_df.empty:
            del_budget_cat = st.selectbox("Select Category to Delete Budget", budgets_df['Category'])
            if st.button("Delete Category Budget"):
                delete_budget(conn, cursor, del_budget_cat)
                st.success(f"Deleted budget for {del_budget_cat}")
                st.experimental_rerun()

        st.write("### Total Budget")
        total_budget = get_total_budget(cursor)
        st.metric("Total Budget", f"₹{total_budget:.2f}")

    # ------------------ VISUALIZATIONS ------------------
    elif choice == "Visualizations":
        st.subheader("Expense Visualizations")

        expenses_by_category = get_expenses_by_category(cursor)

        if expenses_by_category:
            fig1, ax1 = plt.subplots()
            ax1.pie(
                expenses_by_category.values(), 
                labels=expenses_by_category.keys(),
                autopct='%1.1f%%'
            )
            ax1.set_title('Expenses by Category')
            st.pyplot(fig1)

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

        st.write("### Total Budget vs Total Expenses")
        total_budget = get_total_budget(cursor)
        total_expenses = get_total_expenses(cursor)

        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.bar(['Total Budget', 'Total Expenses'], [total_budget, total_expenses], color=['green', 'red'])
        ax3.set_ylabel('Amount (₹)')
        ax3.set_title('Total Budget vs Total Expenses')

        st.pyplot(fig3)

    # ------------------ EXPORT DATA ------------------
    elif choice == "Export Data":
        st.subheader("Export Expense Data")
        csv_file = export_expenses_to_csv(cursor)
        st.download_button(
            label="Download Expense Data",
            data=csv_file,
            file_name="expenses.csv",
            mime="text/csv"
        )

    conn.close()

if __name__ == "__main__":
    main()
