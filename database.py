import sqlite3
from datetime import datetime, timezone


def create_connection():
    return sqlite3.connect("split_expense.db")


# noinspection PyBroadException
def check_database_structure():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        required_tables = {
            "admin_profile": ["profile_id", "total_assets", "name", "contact"],
            "expense_shares": ["expense_id", "profile_id", "share_type", "share_value"],
            "expenses": ["expense_id", "group_id", "payee_id", "amount", "description", "date"],
            "group_members": ["group_id", "profile_id"],
            "groups": ["group_id", "name", "last_expense_time"],
            "member_debts_assets": ["group_id", "receiver_id", "payee_id", "amount"],
            "profiles": ["profile_id", "name", "contact"]
        }
        for table, required_columns in required_tables.items():
            if table in table_names:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                column_names = [column[1] for column in columns]
                if not all(column in column_names for column in required_columns):
                    return False
            else:
                return False
        cursor.execute("SELECT COUNT(*) FROM admin_profile;")
        count = cursor.fetchone()[0]
        if count != 1:
            return False
        return True
    except Exception:
        return False
    finally:
        conn.close()


def initialize_db():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS admin_profile (
                            profile_id INTEGER NOT NULL,
                            total_assets INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            contact TEXT NOT NULL)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS expense_shares (
                            expense_id INTEGER,
                            profile_id INTEGER,
                            share_type TEXT NOT NULL,
                            share_value REAL NOT NULL,
                            PRIMARY KEY (expense_id, profile_id),
                            FOREIGN KEY (expense_id) REFERENCES expenses (expense_id),
                            FOREIGN KEY (profile_id) REFERENCES profiles (profile_id))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
                            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            group_id INTEGER,
                            payee_id INTEGER,
                            amount REAL NOT NULL,
                            description TEXT NOT NULL,
                            date TEXT NOT NULL,
                            FOREIGN KEY (group_id) REFERENCES groups (group_id),
                            FOREIGN KEY (payee_id) REFERENCES profiles (profile_id))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS group_members (
                            group_id INTEGER,
                            profile_id INTEGER,
                            PRIMARY KEY (group_id, profile_id),
                            FOREIGN KEY (group_id) REFERENCES groups (group_id),
                            FOREIGN KEY (profile_id) REFERENCES profiles (profile_id))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS groups (
                            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            last_expense_time TEXT NOT NULL)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS member_debts_assets (
                            group_id INTEGER,
                            receiver_id INTEGER,
                            payee_id INTEGER,
                            amount REAL NOT NULL,
                            PRIMARY KEY (group_id, receiver_id, payee_id),
                            FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
                            FOREIGN KEY (receiver_id) REFERENCES profiles(profile_id),
                            FOREIGN KEY (payee_id) REFERENCES profiles(profile_id))""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS profiles (
                        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        contact TEXT NOT NULL)""")

    conn.commit()
    conn.close()


# noinspection SqlWithoutWhere
def add_admin_profile(name, contact):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_profile")
    cursor.execute("INSERT INTO profiles (name, contact) VALUES (?, ?)", (name, contact))
    admin_id = cursor.lastrowid
    cursor.execute("INSERT INTO admin_profile (profile_id, total_assets, name, contact) VALUES (?, 0, ?, ?)",
                   (admin_id, name, contact))
    conn.commit()
    conn.close()


def get_admin_id():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]
    conn.close()
    return admin_profile_id


def get_admin_assets():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT total_assets from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]
    conn.close()
    return admin_profile_id


def get_admin_name():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]
    conn.close()
    return admin_profile_id


def add_profile(name, contact):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO profiles (name, contact) VALUES (?, ?)", (name, contact))
    conn.commit()
    conn.close()


def get_profiles():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id, name, contact FROM profiles")
    profiles = cursor.fetchall()
    profiles = [(profile_id, name, contact) for profile_id, name, contact in profiles]
    conn.close()
    return profiles


def get_profile_by_id(profile_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,))
    profile = cursor.fetchone()
    conn.close()
    return profile


def get_profile_name(profile_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,))
    profile_name = cursor.fetchall()[0][1]
    conn.close()
    return profile_name


def get_profile_id(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id FROM profiles WHERE name = ?", (name,))
    profile_id = cursor.fetchone()[0]
    conn.close()
    return profile_id


def get_members(group_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.profile_id, p.name, p.contact
                            FROM profiles p
                            JOIN group_members gm ON p.profile_id = gm.profile_id
                            WHERE gm.group_id = ?""", (group_id,))
    profiles = cursor.fetchall()
    conn.close()
    return profiles


def group_exists():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM groups;")
    count = cursor.fetchone()[0]
    if count > 0:
        return True
    else:
        return False


def add_group(name, member_ids):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO groups (name, last_expense_time) VALUES (?, datetime('now'))",
                   (name,))
    group_id = cursor.lastrowid
    for member_id in member_ids:
        cursor.execute("INSERT INTO group_members (group_id, profile_id) VALUES (?, ?)",
                       (group_id, member_id))
        for payee_id in member_ids:
            if member_id != payee_id:
                cursor.execute("INSERT INTO member_debts_assets (group_id, receiver_id, payee_id, amount) "
                               "VALUES (?, ?, ?, 0)", (group_id, member_id, payee_id))

    conn.commit()
    conn.close()


def get_groups():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, name FROM groups ORDER BY last_expense_time DESC")
    groups = cursor.fetchall()
    groups = {name: group_id for group_id, name in groups}
    conn.close()
    return groups


def get_group_name(group_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM groups WHERE group_id = ?", (group_id,))
    group_name = cursor.fetchone()[0]
    conn.close()
    return group_name


def get_group_id(name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM groups WHERE name = ?", (name,))
    group_id = cursor.fetchone()[0]
    conn.close()
    return group_id


def get_group_expenses(group_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE group_id = ? ORDER BY date DESC", (group_id,))
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def get_group_id_expense_id(expense_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM expenses WHERE expense_id = ?", (expense_id,))
    group_id = cursor.fetchone()[0]
    conn.close()
    return group_id


def get_expense(expense_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE expense_id = ?", (expense_id,))
    expense = cursor.fetchall()[0]
    conn.close()
    return expense


def get_profile_involved(expense_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expense_shares WHERE expense_id = ?", (expense_id,))
    profile_involved_dict = cursor.fetchall()
    profile_involved_dict = {profile_id: share_value for expense_id, profile_id, share_type, share_value in
                             profile_involved_dict}
    conn.close()
    return profile_involved_dict


def add_expense(group_id, payee_id, amount, description, member_ids):
    one_person_share = amount / len(member_ids)
    one_person_share = round(one_person_share, 2)
    amount = one_person_share * len(member_ids)
    amount = round(amount, 2)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]
    if payee_id == admin_profile_id:
        cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets + ?, 2) WHERE profile_id = ?",
                       (amount, admin_profile_id))
    cursor.execute("INSERT INTO expenses (group_id, payee_id, amount, description, date) VALUES (?, ?, ?, ?, "
                   "datetime('now'))", (group_id, payee_id, amount, description))
    cursor.execute("UPDATE groups SET last_expense_time = datetime('now') WHERE group_id = ?", (group_id,))
    expense_id = cursor.lastrowid
    for member_id in member_ids:
        cursor.execute(
            "INSERT INTO expense_shares (expense_id, profile_id, share_type, share_value) VALUES (?, ?, 'equal', ?)",
            (expense_id, member_id, one_person_share))
        if payee_id != member_id:
            change_amount_member_debts_assets(cursor, group_id, payee_id, member_id, one_person_share)
        if admin_profile_id == member_id:
            cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets - ?, 2) WHERE profile_id = ?",
                           (one_person_share, admin_profile_id))
    conn.commit()
    conn.close()


def update_expense(expense_id, new_payee_id, new_amount, new_description, new_member_ids):
    new_share = new_amount / len(new_member_ids)
    new_share = round(new_share, 2)
    new_amount = new_share * len(new_member_ids)
    new_amount = round(new_amount, 2)

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT profile_id from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]

    cursor.execute("SELECT group_id, payee_id, amount FROM expenses WHERE expense_id = ?", (expense_id,))
    group_old_payee_id_amount = cursor.fetchone()
    group_id = group_old_payee_id_amount[0]
    old_payee_id = group_old_payee_id_amount[1]
    old_amount = group_old_payee_id_amount[2]
    if old_payee_id == admin_profile_id:
        cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets - ?, 2) WHERE profile_id = ?",
                       (old_amount, admin_profile_id))

    cursor.execute("SELECT profile_id FROM expense_shares WHERE expense_id = ?", (expense_id,))
    old_member_ids = cursor.fetchall()
    old_member_ids = [i[0] for i in old_member_ids]
    cursor.execute("SELECT share_value FROM expense_shares WHERE expense_id = ?", (expense_id,))
    old_share = cursor.fetchone()[0]
    for old_member_id in old_member_ids:
        if old_payee_id != old_member_id:
            change_amount_member_debts_assets(cursor, group_id, old_payee_id, old_member_id, old_share * -1)
        if old_member_id == admin_profile_id:
            cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets + ?, 2) WHERE profile_id = ?",
                           (old_share, admin_profile_id))
    cursor.execute("DELETE FROM expense_shares WHERE expense_id = ?", (expense_id,))
    for new_member_id in new_member_ids:
        cursor.execute("INSERT INTO expense_shares (expense_id, profile_id, share_type, share_value) VALUES (?, ?, "
                       "'equal', ?)", (expense_id, new_member_id, new_share))
        if new_payee_id != new_member_id:
            change_amount_member_debts_assets(cursor, group_id, new_payee_id, new_member_id, new_share)
        if new_member_id == admin_profile_id:
            cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets - ?, 2) WHERE profile_id = ?",
                           (new_share, admin_profile_id))
    cursor.execute("UPDATE expenses SET payee_id = ?, amount = ?, description = ? WHERE expense_id = ?",
                   (new_payee_id, new_amount, new_description, expense_id))
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]
    cursor.execute("SELECT group_id, payee_id, amount from expenses WHERE expense_id = ?", (expense_id,))
    group_receiver_id = cursor.fetchone()
    group_id = group_receiver_id[0]
    payee_id = group_receiver_id[1]
    amount = group_receiver_id[2]
    if payee_id == admin_profile_id:
        cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets - ?, 2) WHERE profile_id = ?",
                       (amount, admin_profile_id))

    cursor.execute("SELECT share_value from expense_shares WHERE expense_id = ?", (expense_id,))
    share_value = cursor.fetchone()[0]
    cursor.execute("SELECT profile_id from expense_shares WHERE expense_id = ?", (expense_id,))
    profiles_id = cursor.fetchall()
    profiles_id = [i[0] for i in profiles_id]
    for profile_id in profiles_id:
        if payee_id != profile_id:
            change_amount_member_debts_assets(cursor, group_id, payee_id, profile_id, share_value * -1)
        if profile_id == admin_profile_id:
            cursor.execute("UPDATE admin_profile SET total_assets = round(total_assets + ?, 2) WHERE profile_id = ?",
                           (share_value, admin_profile_id))
    cursor.execute("DELETE FROM expenses WHERE expense_id = ?", (expense_id,))
    cursor.execute("DELETE FROM expense_shares WHERE expense_id = ?", (expense_id,))
    conn.commit()
    conn.close()


def update_member_debts_assets(group_id, receiver_id, payee_id, amount):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE member_debts_assets SET amount = ? WHERE group_id = ? AND receiver_id = ? AND payee_id = ?",
                   (round(amount, 2), group_id, receiver_id, payee_id))
    conn.commit()
    conn.close()


def amount_0_member_debts_assets(group_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE member_debts_assets SET amount = 0 WHERE group_id = ?", (group_id,))
    conn.commit()
    conn.close()


def change_amount_member_debts_assets(cursor, group_id, receiver_id, payee_id, increment_amount):
    cursor.execute("UPDATE member_debts_assets SET amount = round(amount + ?, 2) WHERE group_id = ? AND receiver_id = "
                   "? AND payee_id = ?", (increment_amount, group_id, receiver_id, payee_id))


def get_member_debts_assets(group_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member_debts_assets WHERE group_id = ? AND amount > 0 ORDER BY receiver_id",
                   (group_id,))
    member_debts_assets = cursor.fetchall()
    conn.close()
    return member_debts_assets


def utc_to_local(utc_date_str):
    utc_time = datetime.strptime(utc_date_str, '%Y-%m-%d %H:%M:%S')
    utc_time = utc_time.replace(tzinfo=timezone.utc)
    local_time_with_tz = datetime.now().astimezone()
    local_offset = local_time_with_tz.utcoffset()
    local_time = utc_time + local_offset
    return local_time.strftime("%d-%m-%Y %I:%M %p")
