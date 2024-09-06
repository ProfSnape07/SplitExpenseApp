import os
import sqlite3
from datetime import datetime, timezone

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ddl = {
    "admin_profile": """
                    CREATE TABLE admin_profile (
                            profile_id INTEGER NOT NULL,
                            total_assets TEXT NOT NULL,
                            name TEXT NOT NULL,
                            contact TEXT NOT NULL)""",
    "expense_shares": """
                    CREATE TABLE expense_shares (
                            expense_id INTEGER,
                            profile_id INTEGER,
                            share_type TEXT NOT NULL,
                            share_value TEXT NOT NULL,
                            PRIMARY KEY (expense_id, profile_id),
                            FOREIGN KEY (expense_id) REFERENCES expenses (expense_id),
                            FOREIGN KEY (profile_id) REFERENCES profiles (profile_id))""",
    "expenses": """
                    CREATE TABLE expenses (
                            expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            group_id INTEGER,
                            payee_id INTEGER,
                            amount TEXT NOT NULL,
                            description TEXT NOT NULL,
                            date TEXT NOT NULL,
                            FOREIGN KEY (group_id) REFERENCES groups (group_id),
                            FOREIGN KEY (payee_id) REFERENCES profiles (profile_id))""",
    "group_members": """
                    CREATE TABLE group_members (
                            group_id INTEGER,
                            profile_id INTEGER,
                            PRIMARY KEY (group_id, profile_id),
                            FOREIGN KEY (group_id) REFERENCES groups (group_id),
                            FOREIGN KEY (profile_id) REFERENCES profiles (profile_id))""",
    "groups": """
                    CREATE TABLE groups (
                            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            last_expense_time TEXT NOT NULL)""",
    "member_debts_assets": """
                    CREATE TABLE member_debts_assets (
                            group_id INTEGER,
                            receiver_id INTEGER,
                            payee_id INTEGER,
                            amount TEXT NOT NULL,
                            PRIMARY KEY (group_id, receiver_id, payee_id),
                            FOREIGN KEY (group_id) REFERENCES groups(group_id) ON DELETE CASCADE,
                            FOREIGN KEY (receiver_id) REFERENCES profiles(profile_id),
                            FOREIGN KEY (payee_id) REFERENCES profiles(profile_id))""",
    "miscellaneous": """
                    CREATE TABLE miscellaneous (
                            key TEXT NOT NULL,
                            value TEXT NOT NULL)""",
    "profiles": """
                    CREATE TABLE profiles (
                        profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        contact TEXT NOT NULL)"""}


def create_connection():
    return sqlite3.connect("split_expense.db")


def clean_sql(sql_statement):
    return ' '.join(sql_statement.split()).strip().lower()


# noinspection PyBroadException
def check_database_structure():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        for table_name, expected_ddl in ddl.items():
            expected_ddl_cleaned = clean_sql(expected_ddl)

            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            existing_ddl = cursor.fetchone()
            if existing_ddl is None:
                return False

            existing_ddl = existing_ddl[0]
            existing_ddl_cleaned = clean_sql(existing_ddl)

            if existing_ddl_cleaned != expected_ddl_cleaned:
                return False

        cursor.execute("SELECT COUNT(*) FROM admin_profile;")
        count = cursor.fetchone()[0]
        if count != 1:
            return False
        cursor.execute("SELECT COUNT(*) FROM miscellaneous;")
        count = cursor.fetchone()[0]
        if count != 1:
            return False

        return True
    except Exception:
        return False
    finally:
        conn.close()


def check_password_required():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM miscellaneous where key='app_name';")
    value = cursor.fetchone()
    if value:
        conn.close()
        return False
    else:
        conn.close()
        return True


def check_password(key):
    dict_key = "app_name"
    dict_key = ecb_mode_encryption(key, dict_key)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM miscellaneous where key = ?;", (dict_key,))
    value = cursor.fetchone()
    if value:
        conn.close()
        return True
    else:
        conn.close()
        return False


def initialize_db():
    conn = create_connection()
    cursor = conn.cursor()
    for table_ddl in ddl.values():
        table_ddl = clean_sql(table_ddl)
        cursor.execute(table_ddl)
    conn.commit()
    conn.close()


# noinspection SqlWithoutWhere
def add_admin_profile(name, contact, key):
    total_assets = "0"
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_profile")
    if key:
        name = ecb_mode_encryption(key, name)
        contact = encrypt_data(key, contact)
        total_assets = encrypt_data(key, total_assets)

    cursor.execute("INSERT INTO profiles (name, contact) VALUES (?, ?)", (name, contact))
    admin_id = cursor.lastrowid
    cursor.execute("INSERT INTO admin_profile (profile_id, total_assets, name, contact) VALUES (?, ?, ?, ?)",
                   (admin_id, total_assets, name, contact))
    conn.commit()
    conn.close()


def add_miscellaneous(dict_key, dict_value, key):
    if key:
        dict_key = ecb_mode_encryption(key, dict_key)
        dict_value = encrypt_data(key, dict_value)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO miscellaneous (key, value) VALUES (?, ?)", (dict_key, dict_value))
    conn.commit()
    conn.close()


def get_admin_id():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id from admin_profile")
    admin_profile_id = cursor.fetchall()[0][0]
    conn.close()
    return admin_profile_id


def get_admin_assets(key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT total_assets from admin_profile")
    admin_assets = cursor.fetchone()[0]
    conn.close()
    if key:
        admin_assets = decrypt_data(key, admin_assets)
    admin_assets = float(admin_assets)
    return admin_assets


def get_admin_name(key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name from admin_profile")
    admin_profile_name = cursor.fetchall()[0][0]
    conn.close()
    if key:
        admin_profile_name = ecb_mode_decryption(key, admin_profile_name)
    return admin_profile_name


def add_profile(name, contact, key):
    if key:
        name = ecb_mode_encryption(key, name)
        contact = encrypt_data(key, contact)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO profiles (name, contact) VALUES (?, ?)", (name, contact))
    conn.commit()
    conn.close()


def get_profiles(key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id, name, contact FROM profiles")
    profiles = cursor.fetchall()
    profiles = [(profile_id, name, contact) for profile_id, name, contact in profiles]
    conn.close()
    if key:
        profiles = [(i[0], ecb_mode_decryption(key, i[1]), decrypt_data(key, i[2])) for i in profiles]
    return profiles


def get_profile_by_id(profile_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE profile_id = ?", (profile_id,))
    profile = cursor.fetchone()
    conn.close()
    if key:
        profile = (profile[0], ecb_mode_decryption(key, profile[1]), decrypt_data(key, profile[2]))
    return profile


def get_profile_name(profile_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM profiles WHERE profile_id = ?", (profile_id,))
    profile_name = cursor.fetchone()[0]
    conn.close()
    if key:
        profile_name = ecb_mode_decryption(key, profile_name)
    return profile_name


def get_members(group_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT p.profile_id, p.name, p.contact
                            FROM profiles p
                            JOIN group_members gm ON p.profile_id = gm.profile_id
                            WHERE gm.group_id = ?""", (group_id,))
    profiles = cursor.fetchall()
    conn.close()
    if key:
        profiles = [(i[0], ecb_mode_decryption(key, i[1]), decrypt_data(key, i[2])) for i in profiles]
    return profiles


def add_group(name, member_ids, key):
    if key:
        name = ecb_mode_encryption(key, name)

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO groups (name, last_expense_time) VALUES (?, datetime('now'))", (name,))
    group_id = cursor.lastrowid
    for member_id in member_ids:
        cursor.execute("INSERT INTO group_members (group_id, profile_id) VALUES (?, ?)", (group_id, member_id))
        for payee_id in member_ids:
            if member_id != payee_id:
                zero = "0"
                if key:
                    zero = encrypt_data(key, zero)
                cursor.execute("INSERT INTO member_debts_assets (group_id, receiver_id, payee_id, amount) "
                               "VALUES (?, ?, ?, ?)", (group_id, member_id, payee_id, zero))

    conn.commit()
    conn.close()


def get_groups(key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, name FROM groups ORDER BY last_expense_time DESC")
    groups = cursor.fetchall()
    groups = {name: group_id for group_id, name in groups}
    conn.close()
    if key:
        groups_decrypted = {ecb_mode_decryption(key, name): group_id for name, group_id in groups.items()}
        groups = groups_decrypted
    return groups


def get_group_name(group_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM groups WHERE group_id = ?", (group_id,))
    group_name = cursor.fetchone()[0]
    conn.close()
    if key:
        group_name = ecb_mode_decryption(key, group_name)
    return group_name


def get_group_expenses(group_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE group_id = ? ORDER BY date DESC", (group_id,))
    expenses = cursor.fetchall()
    conn.close()
    if key:
        expenses = [(i[0], i[1], i[2], float(decrypt_data(key, i[3])), decrypt_data(key, i[4]), i[5]) for i in expenses]
    else:
        expenses = [(i[0], i[1], i[2], float(i[3]), i[4], i[5]) for i in expenses]
    return expenses


def get_group_id_expense_id(expense_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id FROM expenses WHERE expense_id = ?", (expense_id,))
    group_id = cursor.fetchone()[0]
    conn.close()
    return group_id


def get_expense(expense_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE expense_id = ?", (expense_id,))
    expense = cursor.fetchone()
    conn.close()
    if key:
        expense = (
            expense[0], expense[1], expense[2], float(decrypt_data(key, expense[3])), decrypt_data(key, expense[4]),
            expense[5])
    else:
        expense = (expense[0], expense[1], expense[2], float(expense[3]), expense[4], expense[5])

    return expense


def get_profile_involved(expense_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id, share_value FROM expense_shares WHERE expense_id = ?", (expense_id,))
    profile_involved_dict = cursor.fetchall()
    profile_involved_dict = {profile_id: share_value for profile_id, share_value in profile_involved_dict}
    conn.close()
    if key:
        profile_involved_dict_decrypted = {profile_id: float(decrypt_data(key, share_value)) for profile_id, share_value
                                           in profile_involved_dict.items()}
    else:
        profile_involved_dict_decrypted = {profile_id: float(share_value) for profile_id, share_value in
                                           profile_involved_dict.items()}
    profile_involved_dict = profile_involved_dict_decrypted
    return profile_involved_dict


def add_expense(group_id, payee_id, amount, description, member_ids, key):
    one_person_share = amount / len(member_ids)
    one_person_share_float = round(one_person_share, 2)
    amount = one_person_share_float * len(member_ids)
    amount = amount_float = round(amount, 2)
    amount = str(amount)
    if key:
        amount = encrypt_data(key, amount)
        description = encrypt_data(key, description)

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT profile_id, total_assets from admin_profile")
    admin_profile_id, admin_assets = cursor.fetchone()
    if key:
        admin_assets = decrypt_data(key, admin_assets)
    admin_assets = float(admin_assets)
    if payee_id == admin_profile_id:
        admin_assets += amount_float
        admin_assets = round(admin_assets, 2)
        admin_assets_str = str(admin_assets)
        if key:
            admin_assets_str = encrypt_data(key, admin_assets_str)
        cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                       (admin_assets_str, admin_profile_id))

    cursor.execute("UPDATE groups SET last_expense_time = datetime('now') WHERE group_id = ?", (group_id,))
    cursor.execute("INSERT INTO expenses (group_id, payee_id, amount, description, date) VALUES (?, ?, ?, ?, "
                   "datetime('now'))", (group_id, payee_id, amount, description))
    expense_id = cursor.lastrowid

    for member_id in member_ids:
        share_type = "equal"
        if key:
            one_person_share = encrypt_data(key, str(one_person_share_float))
            share_type = encrypt_data(key, share_type)
        cursor.execute(
            "INSERT INTO expense_shares (expense_id, profile_id, share_type, share_value) VALUES (?, ?, ?, ?)",
            (expense_id, member_id, share_type, one_person_share))
        if payee_id != member_id:
            change_amount_member_debts_assets(cursor, group_id, payee_id, member_id, one_person_share_float, key)
        if admin_profile_id == member_id:
            admin_assets -= one_person_share_float
            admin_assets = round(admin_assets, 2)
            admin_assets_str = str(admin_assets)
            if key:
                admin_assets_str = encrypt_data(key, admin_assets_str)

            cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                           (admin_assets_str, admin_profile_id))
    conn.commit()
    conn.close()


def update_expense(expense_id, new_payee_id, new_amount, new_description, new_member_ids, key):
    new_share = new_amount / len(new_member_ids)
    new_share_float = round(new_share, 2)
    new_amount = new_share_float * len(new_member_ids)
    new_amount = new_amount_float = round(new_amount, 2)
    new_amount = str(new_amount)
    if key:
        new_amount = encrypt_data(key, new_amount)
        new_description = encrypt_data(key, new_description)

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT profile_id, total_assets from admin_profile")
    admin_profile_id, admin_assets = cursor.fetchone()
    if key:
        admin_assets = decrypt_data(key, admin_assets)
    admin_assets = float(admin_assets)

    cursor.execute("SELECT group_id, payee_id, amount FROM expenses WHERE expense_id = ?", (expense_id,))
    group_old_payee_id_amount = cursor.fetchone()
    group_id = group_old_payee_id_amount[0]
    old_payee_id = group_old_payee_id_amount[1]
    old_amount = group_old_payee_id_amount[2]
    if key:
        old_amount = decrypt_data(key, old_amount)
    old_amount = float(old_amount)
    if old_payee_id == admin_profile_id:
        admin_assets -= old_amount
        admin_assets = round(admin_assets, 2)
        admin_assets_str = str(admin_assets)
        if key:
            admin_assets_str = encrypt_data(key, admin_assets_str)
        cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                       (admin_assets_str, admin_profile_id))

    cursor.execute("SELECT profile_id FROM expense_shares WHERE expense_id = ?", (expense_id,))
    old_member_ids = cursor.fetchall()
    old_member_ids = [i[0] for i in old_member_ids]
    cursor.execute("SELECT share_value FROM expense_shares WHERE expense_id = ?", (expense_id,))
    old_share = cursor.fetchone()[0]
    if key:
        old_share = decrypt_data(key, old_share)
    old_share = float(old_share)
    for old_member_id in old_member_ids:
        if old_payee_id != old_member_id:
            change_amount_member_debts_assets(cursor, group_id, old_payee_id, old_member_id, old_share * -1, key)
        if old_member_id == admin_profile_id:
            admin_assets += old_share
            admin_assets = round(admin_assets, 2)
            admin_assets_str = str(admin_assets)
            if key:
                admin_assets_str = encrypt_data(key, admin_assets_str)
            cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                           (admin_assets_str, admin_profile_id))
    cursor.execute("DELETE FROM expense_shares WHERE expense_id = ?", (expense_id,))

    if new_payee_id == admin_profile_id:
        admin_assets += new_amount_float
        admin_assets = round(admin_assets, 2)
        admin_assets_str = str(admin_assets)
        if key:
            admin_assets_str = encrypt_data(key, admin_assets_str)
        cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                       (admin_assets_str, admin_profile_id))

    for new_member_id in new_member_ids:
        share_type = "equal"
        if key:
            new_share = encrypt_data(key, str(new_share_float))
            share_type = encrypt_data(key, share_type)
        cursor.execute("INSERT INTO expense_shares (expense_id, profile_id, share_type, share_value) VALUES (?, ?, ?, "
                       "?)", (expense_id, new_member_id, share_type, new_share))
        if new_payee_id != new_member_id:
            change_amount_member_debts_assets(cursor, group_id, new_payee_id, new_member_id, new_share_float, key)
        if new_member_id == admin_profile_id:
            admin_assets -= new_share_float
            admin_assets = round(admin_assets, 2)
            admin_assets_str = str(admin_assets)
            if key:
                admin_assets_str = encrypt_data(key, admin_assets_str)
            cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                           (admin_assets_str, admin_profile_id))
    cursor.execute("UPDATE expenses SET payee_id = ?, amount = ?, description = ? WHERE expense_id = ?",
                   (new_payee_id, new_amount, new_description, expense_id))
    conn.commit()
    conn.close()


def delete_expense(expense_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT profile_id, total_assets from admin_profile")
    admin_profile_id, admin_assets = cursor.fetchone()
    if key:
        admin_assets = decrypt_data(key, admin_assets)
    admin_assets = float(admin_assets)
    cursor.execute("SELECT group_id, payee_id, amount from expenses WHERE expense_id = ?", (expense_id,))
    group_receiver_id = cursor.fetchone()
    group_id = group_receiver_id[0]
    payee_id = group_receiver_id[1]
    amount = group_receiver_id[2]
    if key:
        amount = decrypt_data(key, amount)
    amount = float(amount)

    if payee_id == admin_profile_id:
        admin_assets -= amount
        admin_assets = round(admin_assets, 2)
        admin_assets_str = str(admin_assets)
        if key:
            admin_assets_str = encrypt_data(key, admin_assets_str)
        cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                       (admin_assets_str, admin_profile_id))

    cursor.execute("SELECT share_value from expense_shares WHERE expense_id = ?", (expense_id,))
    share_value = cursor.fetchone()[0]
    if key:
        share_value = decrypt_data(key, share_value)
    share_value = float(share_value)
    cursor.execute("SELECT profile_id from expense_shares WHERE expense_id = ?", (expense_id,))
    profiles_id = cursor.fetchall()
    profiles_id = [i[0] for i in profiles_id]
    for profile_id in profiles_id:
        if payee_id != profile_id:
            change_amount_member_debts_assets(cursor, group_id, payee_id, profile_id, share_value * -1, key)
        if profile_id == admin_profile_id:
            admin_assets += share_value
            admin_assets = round(admin_assets, 2)
            admin_assets_str = str(admin_assets)
            if key:
                admin_assets_str = encrypt_data(key, admin_assets_str)
            cursor.execute("UPDATE admin_profile SET total_assets = ? WHERE profile_id = ?",
                           (admin_assets_str, admin_profile_id))
    cursor.execute("DELETE FROM expenses WHERE expense_id = ?", (expense_id,))
    cursor.execute("DELETE FROM expense_shares WHERE expense_id = ?", (expense_id,))
    conn.commit()
    conn.close()


def update_member_debts_assets(group_id, receiver_id, payee_id, amount: float, key):
    amount = round(amount, 2)
    amount = str(amount)
    if key:
        amount = encrypt_data(key, amount)
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE member_debts_assets SET amount = ? WHERE group_id = ? AND receiver_id = ? AND payee_id = ?",
                   (amount, group_id, receiver_id, payee_id))
    conn.commit()
    conn.close()


def amount_0_member_debts_assets(group_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT group_id, receiver_id, payee_id FROM member_debts_assets WHERE group_id = ?", (group_id,))
    record = cursor.fetchall()
    for group_id, receiver_id, payee_id in record:
        zero = "0"
        if key:
            zero = encrypt_data(key, zero)
        cursor.execute("UPDATE member_debts_assets SET amount = ? WHERE group_id = ? AND receiver_id = ? AND payee_id "
                       "= ?", (zero, group_id, receiver_id, payee_id))
    conn.commit()
    conn.close()


def change_amount_member_debts_assets(cursor, group_id, receiver_id, payee_id, increment_amount, key):
    cursor.execute("SELECT amount FROM member_debts_assets WHERE group_id = ? AND receiver_id = ? AND payee_id = ?",
                   (group_id, receiver_id, payee_id))
    old_amount = cursor.fetchone()[0]
    if key:
        old_amount = decrypt_data(key, old_amount)
    old_amount = float(old_amount)
    new_amount = old_amount + increment_amount
    new_amount = round(new_amount, 2)
    new_amount = str(new_amount)
    if key:
        new_amount = encrypt_data(key, new_amount)

    cursor.execute("UPDATE member_debts_assets SET amount = ? WHERE group_id = ? AND receiver_id = ? AND payee_id = ?",
                   (new_amount, group_id, receiver_id, payee_id))


def get_member_debts_assets(group_id, key):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member_debts_assets WHERE group_id = ? ORDER BY receiver_id", (group_id,))
    member_debts_assets = cursor.fetchall()
    conn.close()
    if key:
        member_debts_assets = [(i[0], i[1], i[2], float(decrypt_data(key, i[3]))) for i in member_debts_assets]
    else:
        member_debts_assets = [(i[0], i[1], i[2], float(i[3])) for i in member_debts_assets]
    member_debts_assets = [i for i in member_debts_assets if i[3] != 0]
    return member_debts_assets


def utc_to_local(utc_date_str):
    utc_time = datetime.strptime(utc_date_str, '%Y-%m-%d %H:%M:%S')
    utc_time = utc_time.replace(tzinfo=timezone.utc)
    local_time_with_tz = datetime.now().astimezone()
    local_offset = local_time_with_tz.utcoffset()
    local_time = utc_time + local_offset
    return local_time.strftime("%d-%m-%Y %I:%M %p")


def pad_data(data):
    block_size = 16
    pad_char = b"+"
    padding_length = (block_size - len(data) % block_size) % block_size
    return data + (pad_char * padding_length)


def encrypt_data(key, plaintext):
    key = bytes.fromhex(key)
    padded_plaintext = pad_data(plaintext.encode())

    # Generate a random 16-byte Initial Vector.
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Return the hex value of IV and the ciphertext combined.
    return (iv + ciphertext).hex()


def decrypt_data(key, encrypted_data):
    key = bytes.fromhex(key)
    try:
        encrypted_data = bytes.fromhex(encrypted_data)
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        plaintext = padded_plaintext.decode().rstrip("+")

        return plaintext

    except UnicodeDecodeError:
        # Exception when decoding with wrong key.
        return None


def ecb_mode_encryption(key, plaintext):
    """
    Encrypt and decrypt group & profile name as the encrypted text need to be same for searching db with those
    parameters.
    :param key:
    :param plaintext:
    :return: ciphertext which will be always same for same key and plaintext pair.
    """
    key = bytes.fromhex(key)
    padded_plaintext = pad_data(plaintext.encode())

    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Return the hex value of IV and the ciphertext combined.
    return ciphertext.hex()


def ecb_mode_decryption(key, encrypted_data):
    key = bytes.fromhex(key)
    try:
        encrypted_data = bytes.fromhex(encrypted_data)

        cipher = Cipher(algorithms.AES(key), modes.ECB())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

        plaintext = padded_plaintext.decode().rstrip("+")

        return plaintext

    except UnicodeDecodeError:
        # Exception when decoding with wrong key.
        return None
