# CHAMA – TABLE BANKING CLI SYSTEM
## User Stories

---

### 1. Creating a Chama

**Title:** Admin creates a new chama

**Business Value:** As an admin, I want to set up a chama with a savings target and deadline, so the group has a shared, trackable goal to work towards.

**Acceptance Criteria:**
- Given a user wants to create a chama
- When the user provides name = "Umoja Chama", target_amount = 2,000,000, frequency = "monthly", deadline = a future date, interest_rate = 0.05
- Then a `Chama` is created with those values, 0 members initially, and a default admin account (username: "admin", password: "pass1234") is automatically added before saving

**Dev Notes:** `Chama.__init__`, `Chama.add_member`. Interest rate is stored on the Chama, not the Member or Loan, since the admin sets it once for the whole group. The default admin is created and appended in the same flow, before the first `save_chama()` call, so no chama is ever saved without at least one working login.

**Design Notes (CLI):** Top-level menu shows only "1. Create chama / 2. Exit" while no chama exists. On creation, prompts run in order: name → target amount → deadline → frequency (validated against daily/weekly/monthly) → interest rate. Confirmation message prints the default admin credentials and instructs the user to log in and change the password.

---

### 2. Admin Adds a Member

**Title:** Admin registers a new member

**Business Value:** As an admin, I want to add members with their own login, so each person's savings and loans are tracked individually.

**Acceptance Criteria:**
- Given an admin is logged in
- When the admin adds a member with name = "Wanjiru", role = "member", password = "pass1234"
- Then a new `Member` exists with name = "Wanjiru", role = "member", a securely hashed password + salt, savings_balance = 0, loan_balance = 0, and must_reset_password = True

**Dev Notes:** `Chama.add_member`, `auth.secure_password`. Passwords are never stored in plain text — `secure_password()` generates a random salt and a PBKDF2-HMAC hash. `must_reset_password` defaults to `True` for every new member, since the admin chooses their initial password and therefore knows it.

**Design Notes (CLI):** Only visible in the logged-in menu when `role == "admin"`. Prompts: name → role → password (masked input via `getpass`).

---

### 3. Forced Password Reset on First Login

**Title:** New account holder must set their own password

**Business Value:** As a member (or the default admin), I want to be forced to choose my own password on first login, so my account isn't left on a password someone else knows.

**Acceptance Criteria:**
- Given a member exists with must_reset_password = True
- When they log in successfully with their assigned password
- Then they are prompted to set a new password before reaching the main menu; must_reset_password becomes False, and they must log in again with the new password

**Dev Notes:** Checked in `main()` immediately after `verify_password()` succeeds, before `logged_in_menu()` is ever called. This is a gate, not a separate menu — the outer login loop simply doesn't proceed to the real menu until the flag is cleared.

**Design Notes (CLI):** After a successful reset, the screen returns to the top-level "Login / Exit" menu rather than continuing straight into the logged-in menu — the member must log in again with their new password.

---

### 4. Member Logs In — Correct Password

**Title:** Member logs in successfully

**Business Value:** As a member, I want to securely access my own account, so my data stays private to me.

**Acceptance Criteria:**
- Given a member "Wanjiru" exists with a stored password
- When she logs in with the correct username and password
- Then login succeeds and she is granted access to the role-appropriate menu

**Dev Notes:** `auth.verify_password` re-derives the hash using the stored salt and compares it to the stored hash — the plain password is never stored or compared directly.

**Design Notes (CLI):** Password entry uses `getpass.getpass()` so it isn't echoed to the terminal.

---

### 5. Member Logs In — Wrong Password

**Title:** Member fails to log in with wrong password

**Business Value:** As a member, I want incorrect login attempts rejected, so my account can't be accessed by guessing.

**Acceptance Criteria:**
- Given a member "Wanjiru" exists with a stored password
- When she logs in with the correct username but wrong password
- Then login fails, access is denied, and no account details are shown

**Dev Notes:** `verify_password` returns `False`; `main()` prints a generic "Invalid username or password" message without revealing whether the username or password was the problem.

---

### 6. Each Member's Expected Contribution

**Title:** Member checks their total expected share

**Business Value:** As a member, I want to know my total expected contribution, so I understand what I'm working towards.

**Acceptance Criteria:**
- Given a chama with target_amount = 2,000,000 and 10 members
- When a member requests their expected contribution
- Then expected_contribution_per_member = 200,000 (target_amount ÷ number of members)

**Dev Notes:** `Chama.expected_contribution_per_member()`. Returns 0 if there are no members yet, to avoid a division-by-zero crash.

---

### 7. Member Checks Expected Amount Per Contribution Cycle

**Title:** Member sees how much to contribute per period

**Business Value:** As a member, I want to know how much to save each cycle (daily/weekly/monthly), so I can pace my contributions instead of guessing.

**Acceptance Criteria:**
- Given a chama with expected_contribution_per_member = 200,000, frequency = "weekly", and 100 days remaining until the deadline
- When a member requests their per-period amount
- Then number_of_periods = 100 // 7 = 14, and expected_amount_per_period = ceil(200,000 / 14) = 14,286

**Dev Notes:** `Chama.number_of_periods()` converts remaining days into cycles based on frequency (daily/weekly/monthly), floored, with a minimum of 1 to avoid division by zero near the deadline. `Chama.expected_amount_per_period()` divides the flat per-member share across those cycles and rounds up with `math.ceil`, so the group's target is reached on or slightly before the deadline, never after.

---

### 8. Member Contributes an Amount

**Title:** Member logs a contribution

**Business Value:** As a member, I want to record what I've contributed, so my balance and history stay accurate.

**Acceptance Criteria:**
- Given a member with savings_balance = 5,000
- When the member contributes 1,000
- Then savings_balance = 6,000, and a `Contribution` record is created with amount = 1,000 and today's date

**Dev Notes:** `Member.contribute()` raises `ValueError` for amounts ≤ 0. Each contribution is appended to `self.contributions`, giving an auditable history rather than just a running total.

---

### 9. Member Checks Personal Progress

**Title:** Member views their own savings and loan status

**Business Value:** As a member, I want a single view of my balance, goal progress, and loan status, so I know exactly where I stand.

**Acceptance Criteria:**
- Given a member with savings_balance = 50,000, expected_contribution_per_member = 200,000, no active loan
- When the member checks their personal progress
- Then they see total_contributed = 50,000, amount_remaining = 150,000, and max_loan_available = 150,000 (3 × savings); if a loan is active, they see the outstanding loan_balance instead of the max-loan figure

**Dev Notes:** Handled in the "My progress" menu option — reads `current_member.savings_balance`, `chama.expected_contribution_per_member()`, and branches on `current_member.is_loan_active()`.

---

### 10. Admin Checks Overall Chama Progress

**Title:** Admin views group-wide progress

**Business Value:** As an admin, I want a summary of the whole chama's progress, so I can track collective performance and see who has outstanding loans.

**Acceptance Criteria:**
- Given a chama with multiple members, some with contributions and some with active loans
- When the admin requests overall progress
- Then the admin sees total_saved (sum across all members), progress_percentage toward the target, and a per-member list showing each member's savings_balance and current loan status (active balance, or "no active loan")

**Dev Notes:** `Chama.total_saved()`, `Chama.progress_percentage()`, plus a loop over `chama.members` checking `is_loan_active()` per member. *Scope note: aggregate figures such as total loans issued and total repaid across the group were descoped for time — the current view is per-member, not pre-aggregated.*

**Design Notes (CLI):** Only visible when `current_member.role == "admin"`.

---

### 11. Member Requests a Loan Within Limit

**Title:** Member borrows within their allowed limit

**Business Value:** As a member, I want to borrow against my savings, so I can access funds without leaving the chama.

**Acceptance Criteria:**
- Given a member with savings_balance = 5,000 and no active loan
- When the member requests a loan of 10,000 (≤ 3 × 5,000) at the chama's interest_rate = 0.05
- Then a `Loan` is created, loan_balance = 10,000 × 1.05 = 10,500, and is_loan_active() returns True

**Dev Notes:** `Member.request_loan(amount, interest_rate)` — interest_rate is passed in from `chama.interest_rate` at the CLI layer, keeping `Member` independent of `Chama` (avoids a circular import). Creates a `Loan` object stored on `self.loan`; `self.loan_balance` is kept as a cached copy for simple serialization.

---

### 12. Member Requests a Loan Above Limit

**Title:** Member is blocked from over-borrowing

**Business Value:** As a member, I want the system to enforce a fair borrowing limit, so no one can drain the group's funds disproportionately.

**Acceptance Criteria:**
- Given a member with savings_balance = 5,000 and no active loan
- When the member requests a loan of 20,000 (> 3 × 5,000)
- Then the request is rejected with `ValueError("Requested amount 20000 exceeds loan limit of 15000")`, and loan_balance remains 0

**Dev Notes:** Validation happens inside `Member.request_loan()` itself, not in the CLI, so the rule is enforced regardless of how the method is called (menu or test).

---

### 13. Member Repays a Loan

**Title:** Member repays part or all of an active loan

**Business Value:** As a member, I want to repay my loan and see it clear once fully paid, so I can borrow again in the future.

**Acceptance Criteria:**
- Given a member with an active loan and loan_balance = 10,500 (10,000 principal + 5% interest)
- When the member repays 10,500
- Then loan_balance = 0, is_loan_active() returns False, and the member is eligible to request a new loan

**Dev Notes:** `Member.repay_loan()` delegates to `Loan.repay()`, which reduces the balance and flips `active` to `False` once it reaches 0. `Member.loan_balance` is refreshed from `self.loan.loan_balance()` after every repayment to keep the cached copy in sync.

---

## CLI Menu Tree (Design Overview)

```
Not logged in:
  1. Create chama   (only shown if no chama exists yet)
  2. Login          (only shown once a chama exists)
  3. Exit

Logged in (all roles):
  1. Contribute
  2. My progress
  3. Request loan
  4. Repay loan
  5. Logout

Logged in (admin only, appended):
  6. Add member
  7. Chama overview
```
