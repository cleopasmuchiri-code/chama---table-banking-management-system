from storage import load_chama, save_chama
import os
import datetime
from models.chama import Chama
from models.member import Member
import getpass
from auth import secure_password, verify_password

CHAMA_FILE = "data/chama.json"


def get_frequency_input():
    valid = {"daily", "weekly", "monthly"}
    while True:
        frequency = (
            input("Contribution frequency (daily/weekly/monthly): ").strip().lower()
        )
        if frequency in valid:
            return frequency
        print("Invalid frequency. Please choose daily, weekly or monthly")


def logged_in_menu(chama, current_member):
    while True:
        print(f"\n--- Welcome {current_member.name} ({current_member.role}) ---")
        print("1. Contribute")
        print("2. My progress")
        print("3. Request loan")
        print("4. Repay loan")
        print("5. Logout")
        if current_member.role == "admin":
            print("6. Add member")
            print("7. Chama overview")

        choice = input("Choose an option: ")

        if choice == "1":
            amount = float(input("Amount to contribute: "))
            try:
                current_member.contribute(amount)
                save_chama(chama, CHAMA_FILE)
                print(f"New balance: {current_member.savings_balance}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "2":
            expected_total = chama.expected_contribution_per_member()
            per_period = chama.expected_amount_per_period()
            print(f"Total contributed: {current_member.savings_balance}")
            print(f"Expected share: {expected_total}")
            print(f"Expected per {chama.frequency.rstrip('ly')} cycle: {per_period}")
            print(f"Remaining: {expected_total - current_member.savings_balance}")
            if current_member.is_loan_active():
                print(f"Active loan balance: {current_member.loan_balance}")
            else:
                print(f"Max loan available: {current_member.savings_balance * 3}")

        elif choice == "3":
            amount = float(input("Loan amount requested: "))
            try:
                current_member.request_loan(amount, chama.interest_rate)
                save_chama(chama, CHAMA_FILE)
                print(f"Loan approved. Balance owed: {current_member.loan_balance}")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "4":
            amount = float(input("Amount to repay: "))
            current_member.repay_loan(amount)
            save_chama(chama, CHAMA_FILE)
            print(f"Remaining loan balance: {current_member.loan_balance}")

        elif choice == "5":
            print("Logged out.")
            return

        elif choice == "6" and current_member.role == "admin":
            name = input("Member name: ")
            role = input("Member role (member/admin): ")
            user_password = getpass.getpass("Enter password: ")
            salt, hashed = secure_password(user_password)
            member = Member(name=name, role=role, salt=salt, password=hashed)
            chama.add_member(member)
            save_chama(chama, CHAMA_FILE)
            print(f"Member {name} added.")

        elif choice == "7" and current_member.role == "admin":
            print(f"Total saved: {chama.total_saved()}")
            print(f"Progress: {chama.progress_percentage():.1f}%")
            for m in chama.members:
                loan_status = (
                    f"loan: {m.loan_balance}"
                    if m.is_loan_active()
                    else "no active loan"
                )
                print(f"  {m.name}: saved {m.savings_balance}, {loan_status}")

        else:
            print("Invalid option, try again.")


def main():
    if os.path.exists(CHAMA_FILE) and os.path.getsize(CHAMA_FILE) > 0:
        chama = load_chama(CHAMA_FILE)
    else:
        chama = None

    while True:
        print("\n--- Chama Menu ---")
        if chama is None:
            print("1. Create chama")
            print("2. Exit")
        else:
            print("1. Login")
            print("2. Exit")
        choice = input("Choose an option: ")

        if chama is None:
            if choice == "1":
                name = input("Chama name: ")
                target_amount = float(input("Target amount: "))
                deadline_str = input("Deadline (YYYY-MM-DD): ")
                frequency = get_frequency_input()
                interest_rate = float(input("Loan interest rate (e.g. 0.05 for 5%): "))
                chama = Chama(
                    name=name,
                    target_amount=target_amount,
                    deadline=datetime.date.fromisoformat(deadline_str),
                    frequency=frequency,
                    interest_rate=interest_rate,
                )

                salt, hashed = secure_password("pass1234")
                default_admin = Member(
                    name="admin", role="admin", salt=salt, password=hashed
                )

                chama.add_member(default_admin)

                save_chama(chama, CHAMA_FILE)
                print(
                    f"Chama '{name}' created with default admin (username: admin, password: pass1234)."
                )
                print("Please log in and change the password.")
                print("Username: admin")
                print("Password: pass1234")

            elif choice == "2":
                print("Goodbye!")
                break
            else:
                print("Invalid option, try again.")

        else:
            if choice == "1":
                username = input("Username: ")
                entered_password = getpass.getpass("Password: ")
                match = next((m for m in chama.members if m.name == username), None)
                if match and verify_password(
                    entered_password, match.salt, match.password
                ):
                    if match.must_reset_password:
                        new_password = getpass.getpass("Set a new password: ")
                        salt, hashed = secure_password(new_password)
                        match.salt = salt
                        match.password = hashed
                        match.must_reset_password = False
                        save_chama(chama, CHAMA_FILE)
                        print("Password updated. Please log in again.")
                    else:
                        logged_in_menu(chama, match)
                else:
                    print("Invalid username or password.")

            elif choice == "2":
                print("Goodbye!")
                break
            else:
                print("Invalid option, try again.")


if __name__ == "__main__":
    main()
