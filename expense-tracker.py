"""
Institute Expense Tracker
=========================
A small command-line program that records the daily operational expenses of a
training institute (stationery, internet bills, refreshments, transport, ...).

Concepts demonstrated
---------------------
* File handling      : expenses are persisted in ``expenses.csv`` (csv module).
* Exception handling : ``FileNotFoundError`` on first start, ``ValueError`` for
                       invalid amounts/dates, plus a few defensive handlers.
* Sets               : a set holds the unique expense categories.
* Comprehensions     : set / dict / list comprehensions build the reports.

CSV format (header row included)::

    date,item,category,amount
"""

import csv
import math
import os
from datetime import date, datetime

CSV_FILE = "expenses.csv"
FIELDNAMES = ["date", "item", "category", "amount"]


# --------------------------------------------------------------------------- #
# File handling
# --------------------------------------------------------------------------- #
def load_expenses(filename=CSV_FILE):
    """Load saved expenses from *filename* and return them as a list of dicts.

    * If the file does not exist, ``FileNotFoundError`` is caught and an empty
      list is returned, so the very first run works without any set-up.
    * Rows that are damaged (missing columns / non-numeric amount) are skipped
      with a warning instead of crashing the whole program.
    """
    expenses = []
    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for line_no, row in enumerate(reader, start=2):  # line 1 = header
                try:
                    expenses.append(
                        {
                            "date": row["date"].strip(),
                            "item": row["item"].strip(),
                            "category": row["category"].strip(),
                            "amount": float(row["amount"]),
                        }
                    )
                except (KeyError, ValueError, AttributeError, TypeError):
                    print(f"  [warning] Skipped damaged row at line {line_no} of {filename}.")
        print(f"Loaded {len(expenses)} saved expense(s) from '{filename}'.")
    except FileNotFoundError:
        print(f"'{filename}' not found. Starting with an empty expense list.")
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        # PermissionError, IsADirectoryError, bad encoding, corrupted CSV, ...
        print(f"[error] Could not read '{filename}' ({error}). Starting with an empty list.")
    return expenses


def save_expense(expense, filename=CSV_FILE):
    """Append one expense to *filename*, writing the header if the file is new/empty."""
    needs_header = not os.path.exists(filename) or os.path.getsize(filename) == 0
    try:
        with open(filename, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            if needs_header:
                writer.writeheader()
            writer.writerow(expense)
        return True
    except OSError as error:  # PermissionError, disk full, read-only folder, ...
        print(f"[error] Could not save to '{filename}': {error}")
        return False


# --------------------------------------------------------------------------- #
# Input helpers (validation)
# --------------------------------------------------------------------------- #
def get_non_empty(prompt):
    """Keep asking until the user types something other than blank spaces."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  This field cannot be empty. Please try again.")


def get_valid_date(prompt):
    """Ask for a date in YYYY-MM-DD format (Enter = today). Re-asks on ValueError."""
    while True:
        text = input(prompt).strip()
        if not text:
            return date.today().isoformat()
        try:
            return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print("  Invalid date. Please use the format YYYY-MM-DD (e.g. 2026-11-15).")


def get_valid_amount(prompt):
    """Ask for a positive number. A ``ValueError`` triggers a re-prompt."""
    while True:
        text = input(prompt).strip().replace(",", "")
        try:
            amount = float(text)  # raises ValueError for "abc", "", "12x" ...
            if math.isnan(amount) or math.isinf(amount) or amount <= 0:
                raise ValueError("amount must be a finite number greater than zero")
            return round(amount, 2)
        except ValueError:
            print("  Invalid amount. Please enter a valid positive number (e.g. 1250 or 99.50).")


# --------------------------------------------------------------------------- #
# Menu actions
# --------------------------------------------------------------------------- #
def add_expense(expenses):
    """Menu option 1 - collect a new expense, store it in memory and in the CSV."""
    print("\n--- Add New Expense ---")
    expense = {
        "date": get_valid_date("Date (YYYY-MM-DD, Enter for today): "),
        "item": get_non_empty("Item name: "),
        "category": get_non_empty("Category: ").title(),  # "transport" == "Transport"
        "amount": get_valid_amount("Amount: "),
    }
    if save_expense(expense):
        expenses.append(expense)
        print(f"Saved: {expense['item']} ({expense['category']}) - {expense['amount']:.2f}")


def show_all_expenses(expenses):
    """Menu option 2 - print every expense in a table and list the unique categories."""
    print("\n--- All Expenses ---")
    if not expenses:
        print("No expenses recorded yet.")
        return

    print(f"{'No.':<5}{'Date':<12}{'Item':<24}{'Category':<16}{'Amount':>10}")
    print("-" * 67)
    for number, e in enumerate(expenses, start=1):
        print(f"{number:<5}{e['date']:<12}{e['item'][:22]:<24}{e['category'][:14]:<16}{e['amount']:>10.2f}")
    print("-" * 67)

    # SET COMPREHENSION -> every category appears only once.
    unique_categories = {e["category"] for e in expenses}
    print(f"Records: {len(expenses)}")
    print(f"Unique categories ({len(unique_categories)}): {', '.join(sorted(unique_categories))}")


def show_totals_by_category(expenses):
    """Menu option 3 - total spending per category (+ grand total)."""
    print("\n--- Total Expenses by Category ---")
    if not expenses:
        print("No expenses recorded yet.")
        return

    unique_categories = {e["category"] for e in expenses}  # set of unique categories
    # DICT COMPREHENSION + generator expression -> {category: total}
    totals = {
        category: sum(e["amount"] for e in expenses if e["category"] == category)
        for category in unique_categories
    }

    print(f"{'Category':<20}{'Total':>12}")
    print("-" * 32)
    for category in sorted(totals):
        print(f"{category:<20}{totals[category]:>12.2f}")
    print("-" * 32)
    print(f"{'GRAND TOTAL':<20}{sum(totals.values()):>12.2f}")


# --------------------------------------------------------------------------- #
# Main program
# --------------------------------------------------------------------------- #
MENU = """
===== Institute Expense Tracker =====
1. Add New Expense
2. Show All Expenses
3. Calculate Total Expenses by Category
4. Exit
"""


def main():
    expenses = load_expenses()
    while True:
        print(MENU)
        try:
            choice = input("Choose an option (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):  # Ctrl+D / Ctrl+C
            print("\nInput closed. Exiting. Your saved expenses are safe in the CSV file.")
            break

        try:
            if choice == "1":
                add_expense(expenses)
            elif choice == "2":
                show_all_expenses(expenses)
            elif choice == "3":
                show_totals_by_category(expenses)
            elif choice == "4":
                print("Goodbye! All expenses are saved in 'expenses.csv'.")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 4.")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled. Returning to the menu.")


if __name__ == "__main__":
    main()
