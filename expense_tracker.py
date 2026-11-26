import os
import json
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

# ---------------- PROJECT SETTINGS ----------------

FILE_NAME = "transactions.csv"
BUDGET_FILE = "budget.json"

COLUMNS = ["id", "type", "amount", "category", "date", "description"]

CATEGORIES = [
    "Food", "Shopping", "Travel", "Education",
    "Bills", "Entertainment", "Health",
    "Salary", "Other Income", "Other"
]


# ---------------- FILE HANDLING ----------------

def load_data():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE_NAME, index=False)
        return df

    try:
        df = pd.read_csv(FILE_NAME)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        print("Warning: Could not read the transaction file.")
        return pd.DataFrame(columns=COLUMNS)


def save_data(df):
    df.to_csv(FILE_NAME, index=False)


def load_budget():
    if os.path.exists(BUDGET_FILE):
        try:
            with open(BUDGET_FILE, "r") as file:
                return json.load(file).get("monthly_budget", 0)
        except (json.JSONDecodeError, OSError):
            return 0
    return 0


def save_budget(amount):
    with open(BUDGET_FILE, "w") as file:
        json.dump({"monthly_budget": amount}, file, indent=4)


# ---------------- INPUT VALIDATION ----------------

def get_amount(message):
    while True:
        try:
            amount = float(input(message))
            if amount <= 0:
                print("Amount must be greater than zero.")
            else:
                return amount
        except ValueError:
            print("Please enter a valid number.")


def get_date():
    while True:
        date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")

        if date == "":
            return datetime.today().strftime("%Y-%m-%d")

        try:
            return datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date. Example: 2026-11-26")


# ---------------- TRANSACTION MANAGEMENT ----------------

def add_transaction():
    df = load_data()

    print("\n1. Income")
    print("2. Expense")

    choice = input("Choose transaction type: ")

    if choice == "1":
        transaction_type = "Income"
    elif choice == "2":
        transaction_type = "Expense"
    else:
        print("Invalid choice.")
        return

    amount = get_amount("Enter amount: ")

    print("\nAvailable categories:")
    print(", ".join(CATEGORIES))

    category = input("Enter category: ").strip().title()

    if not category:
        print("Category cannot be empty.")
        return

    date = get_date()
    description = input("Enter description: ").strip()

    if df.empty:
        new_id = 1
    else:
        new_id = int(pd.to_numeric(df["id"]).max()) + 1

    new_record = {
        "id": new_id,
        "type": transaction_type,
        "amount": amount,
        "category": category,
        "date": date,
        "description": description
    }

    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    save_data(df)

    print("Transaction added successfully!")


def view_transactions():
    df = load_data()

    if df.empty:
        print("\nNo transactions available.")
        return

    print("\nALL TRANSACTIONS")
    print(df.to_string(index=False))


def search_transaction():
    df = load_data()

    if df.empty:
        print("No transactions to search.")
        return

    keyword = input("Enter ID, category or description to search: ").strip()

    if not keyword:
        print("Search value cannot be empty.")
        return

    result = df[
        df["id"].astype(str).str.contains(keyword, case=False, na=False)
        | df["category"].astype(str).str.contains(keyword, case=False, na=False)
        | df["description"].astype(str).str.contains(keyword, case=False, na=False)
    ]

    if result.empty:
        print("No matching transaction found.")
    else:
        print(result.to_string(index=False))


def update_transaction():
    df = load_data()

    if df.empty:
        print("No transactions available.")
        return

    try:
        transaction_id = int(input("Enter transaction ID to update: "))
    except ValueError:
        print("Please enter a valid ID.")
        return

    index = df.index[df["id"] == transaction_id].tolist()

    if not index:
        print("Transaction not found.")
        return

    i = index[0]
    print("Press Enter to keep the existing value.")

    new_amount = input("New amount: ").strip()
    if new_amount:
        try:
            value = float(new_amount)
            if value <= 0:
                print("Amount must be positive.")
                return
            df.at[i, "amount"] = value
        except ValueError:
            print("Invalid amount.")
            return

    new_type = input("New type (Income/Expense): ").strip().title()
    if new_type:
        if new_type not in ["Income", "Expense"]:
            print("Invalid transaction type.")
            return
        df.at[i, "type"] = new_type

    new_category = input("New category: ").strip()
    if new_category:
        df.at[i, "category"] = new_category.title()

    new_date = input("New date (YYYY-MM-DD): ").strip()
    if new_date:
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            df.at[i, "date"] = new_date
        except ValueError:
            print("Invalid date.")
            return

    new_description = input("New description: ").strip()
    if new_description:
        df.at[i, "description"] = new_description

    save_data(df)
    print("Transaction updated successfully!")


def delete_transaction():
    df = load_data()

    if df.empty:
        print("No transactions available.")
        return

    try:
        transaction_id = int(input("Enter transaction ID to delete: "))
    except ValueError:
        print("Please enter a valid ID.")
        return

    if transaction_id not in df["id"].values:
        print("Transaction not found.")
        return

    df = df[df["id"] != transaction_id]
    save_data(df)

    print("Transaction deleted successfully!")


# ---------------- FINANCIAL ANALYSIS ----------------

def show_summary():
    df = load_data()

    if df.empty:
        print("No data available for analysis.")
        return

    income = df.loc[df["type"] == "Income", "amount"].sum()
    expenses = df.loc[df["type"] == "Expense", "amount"].sum()
    balance = income - expenses

    print("\n----- FINANCIAL SUMMARY -----")
    print(f"Total Income:   Rs. {income:.2f}")
    print(f"Total Expenses: Rs. {expenses:.2f}")
    print(f"Current Balance: Rs. {balance:.2f}")

    print("\nCATEGORY-WISE EXPENSES")

    expense_data = df[df["type"] == "Expense"]

    if expense_data.empty:
        print("No expenses recorded.")
    else:
        category_summary = expense_data.groupby("category")["amount"].sum()
        print(category_summary.to_string())

    print("\nMONTHLY ANALYSIS")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["month"] = df["date"].dt.to_period("M")

    monthly = df.pivot_table(
        index="month",
        columns="type",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    print(monthly.to_string())


# ---------------- BUDGET MANAGEMENT ----------------

def set_budget():
    budget = get_amount("Enter your monthly budget: ")
    save_budget(budget)
    print("Monthly budget saved successfully!")


def check_budget():
    df = load_data()
    budget = load_budget()

    if budget <= 0:
        print("Please set your monthly budget first.")
        return

    current_month = datetime.today().strftime("%Y-%m")

    if df.empty:
        spent = 0
    else:
        dates = pd.to_datetime(df["date"], errors="coerce")
        mask = (
            (df["type"] == "Expense")
            & (dates.dt.strftime("%Y-%m") == current_month)
        )
        spent = df.loc[mask, "amount"].sum()

    remaining = budget - spent

    print("\n----- MONTHLY BUDGET -----")
    print(f"Budget:    Rs. {budget:.2f}")
    print(f"Spent:     Rs. {spent:.2f}")
    print(f"Remaining: Rs. {remaining:.2f}")

    if spent > budget:
        print("ALERT: You have exceeded your monthly budget!")
    elif spent >= budget * 0.8:
        print("WARNING: You have used 80% or more of your budget.")
    else:
        print("You are within your budget.")


# ---------------- CHARTS AND VISUALIZATION ----------------

def generate_charts():
    df = load_data()

    if df.empty:
        print("No transactions available for charts.")
        return

    expenses = df[df["type"] == "Expense"].copy()
    income = df[df["type"] == "Income"].copy()

    if not expenses.empty:
        category_data = expenses.groupby("category")["amount"].sum()

        plt.figure(figsize=(8, 6))
        category_data.plot(kind="pie", autopct="%1.1f%%")
        plt.title("Category-wise Expense Distribution")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig("category_expenses.png")
        plt.show()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = df.pivot_table(
        index="month",
        columns="type",
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    if not monthly.empty:
        monthly.plot(kind="bar", figsize=(9, 5))
        plt.title("Monthly Income vs Expenses")
        plt.xlabel("Month")
        plt.ylabel("Amount (Rs.)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("monthly_analysis.png")
        plt.show()

    print("Charts generated and saved as image files.")


# ---------------- AUTOMATIC INSIGHTS ----------------

def generate_insights():
    df = load_data()

    if df.empty:
        print("No data available for insights.")
        return

    income = df.loc[df["type"] == "Income", "amount"].sum()
    expenses = df.loc[df["type"] == "Expense", "amount"].sum()
    balance = income - expenses

    print("\n----- SMART FINANCIAL INSIGHTS -----")

    if expenses > 0:
        expense_data = df[df["type"] == "Expense"]
        highest_category = expense_data.groupby("category")["amount"].sum().idxmax()
        highest_amount = expense_data.groupby("category")["amount"].sum().max()

        print(f"Highest spending category: {highest_category}")
        print(f"Amount spent in this category: Rs. {highest_amount:.2f}")

    if income > 0:
        savings_rate = (balance / income) * 100
        print(f"Savings rate: {savings_rate:.2f}%")

    if balance > 0:
        print("Your recorded income is greater than your expenses.")
    elif balance < 0:
        print("Your recorded expenses are greater than your income.")
    else:
        print("Your recorded income and expenses are equal.")

    check_budget()


# ---------------- MAIN APPLICATION ----------------

def main():
    while True:
        print("\n===================================")
        print(" SMART PERSONAL EXPENSE TRACKER")
        print("===================================")

        print("1. Add Income / Expense")
        print("2. View All Transactions")
        print("3. Search Transaction")
        print("4. Update Transaction")
        print("5. Delete Transaction")
        print("6. Financial Summary")
        print("7. Set Monthly Budget")
        print("8. Check Monthly Budget")
        print("9. Generate Charts")
        print("10. Generate Smart Insights")
        print("11. Exit")

        choice = input("\nEnter your choice (1-11): ").strip()

        try:
            if choice == "1":
                add_transaction()
            elif choice == "2":
                view_transactions()
            elif choice == "3":
                search_transaction()
            elif choice == "4":
                update_transaction()
            elif choice == "5":
                delete_transaction()
            elif choice == "6":
                show_summary()
            elif choice == "7":
                set_budget()
            elif choice == "8":
                check_budget()
            elif choice == "9":
                generate_charts()
            elif choice == "10":
                generate_insights()
            elif choice == "11":
                print("Thank you for using Smart Expense Tracker!")
                break
            else:
                print("Invalid choice. Please select 1 to 11.")

        except (OSError, KeyError, TypeError) as error:
            print("An error occurred:", error)


if __name__ == "__main__":
    main()
