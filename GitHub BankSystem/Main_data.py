import random
import re
import csv
import sqlite3

Data = {}
count = {'count': 1}

def menu(): 
    loadToSQL()
    while True:
        print("\t----------Menu----------\n")
        print("\t1-. Log in")
        print("\t2-. Sign Up")
        print("\t3-. Exit")
        argument = input()
        match argument:
            case '1': logIn()
            case '2': createUser()
            case '3': break
            case _: print('!Wrong Option')

def logIn():
    if not searchUser():
        deleteUser()
        return

    
    while True:
        print("\t----------Menu----------\n")
        print("\t1-. Read an account")
        print("\t2-. Deposit or Withdraw Cash")
        print("\t3-. Delete your account")
        print("\t4-. Log out\n")
        argument  = input()
        match argument:
            case '1': showData()
            case '2': modification()
            case '3': delete()
            case '4': break
            case _: print('!Wrong Option')

def readData():
    
    #User ID | First Name | Last Name | Email Address | Account Type | Account Number | Balance

    global Data

    Data = {
        'name': input("\n Type your Name: "),
        'lastName': input("\n Type your Last Name: "),
    }

    # valid email
    while True: 
        email = input('\n Type your email address: ')
        if is_valid_email(email):
            Data['email'] = email
            break
        else:
            print('Invalid email address. please try again')

    # valid type account
    valid_account_types = ["Checking", "Savings", "Investment", "Credit Card", "Loan", "Mortgage"]
    
    while True: 
        account_type = input('\n What type of account do you want to create? (Checking, Savings, Investment, Credit Card, Loan, Mortgage): ')
        if account_type in valid_account_types:
            Data['account_type'] = account_type
            break
        else:
            print("Invalid account type. Please choose from Checking, Savings, Investment, Credit Card, Loan, Mortgage.")

    Data['balance'] = input('\n How much money do you want to deposit: ')

    # Generate a random account number
    ramNum = int(random.uniform(100000000, 900000000))
    Data['account_number'] = str(ramNum)

    # Set password
    Data['password'] = input("\n Type your password: ")

    # Read the file to search if the user already exists
    user_exists = False
    try:
        with open("User.csv", 'r') as file:
            reader = csv.reader(file)
            for pieces in reader: 
                if len(pieces) < 8: continue
                if (Data['name'] == pieces[1].strip() and
                    Data['lastName'] == pieces[2].strip() and
                    Data['email'] == pieces[3].strip()):
                    Data['user'] = pieces[0].strip()
                    user_exists = True
                    break
    except FileNotFoundError:
        pass
            
    if not user_exists:
        countUsers()
        Data['user'] = str(count['count'])

def showData():
    with open('User.csv', 'r') as file:
        reader = csv.reader(file)
        for pieces in reader:
            if len(pieces) < 8: continue 
            if pieces[0].strip() == Data['user']:  
                Data['name'] = pieces[1]
                Data['lastName'] = pieces[2]
                Data['email'] = pieces[3]
                Data['account_type'] = pieces[4]
                Data['account_number'] = pieces[5]
                Data['balance'] = pieces[6]
                Data['password'] = pieces[7]

    print("\t-------------------------------\n")
    print("\tAccount Type: ", Data['account_type'], "\n")
    print("\tAccount Number: ", Data['account_number'], "\n")
    print("\tName & LastName: ", Data['name'], Data['lastName'], "\n")
    print("\tEmail: ", Data['email'], "\n")
    print("\tBalance: ", Data['balance'], "\n")
    print("\t-------------------------------\n")
        

def createUser():
    readData()
    sortedUsers()
    with open('User.csv', 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')

        balance = float(Data['balance'])
        formatted_balance = f"${balance:.2f}"
        
        writer.writerow([
            Data['user'], Data['name'], Data['lastName'], Data['email'],
            Data['account_type'], Data['account_number'],formatted_balance,Data['password']
        ])
    showData()
    addUserToSQL()

def withDraw():
    global Data 
    balance = float(Data['balance'].strip('$'))
    while(True):
        auxBalance = float(input("How much money do you want to withdraw?"))
        if(auxBalance>balance):
            print("\tYou dont have that money, You have: ",balance)
        else:
            balance-=auxBalance
            op = input("Do you want to withdraw more money?  yes(0)/no(1)")
            if op != 0: break
    Data['balance'] = balance
    updateBalanceCSV()

def deposit():
    global Data
    balance = float(Data['balance'].strip('$'))
    while(True):
        auxBalance = float(input("How much money do you want to deposit?"))
        balance+=auxBalance
        print("\nThe money is going to be available in a couple minutes ")
        op = input("\tDo you want to deposit more money?  yes(0)/no(1)")
        if op != 0: break

    Data['balance'] = balance
    updateBalanceCSV()

def modification():
    global Data
    ask = input("Do you want deposit(1) or withdraw(0) money")
    if(ask == '1'): 
        deposit()
    elif(ask == '0'):
        withDraw()
    else:
        print("¡Wrong Option!")

def searchUser():
    Data['user'] = input('\n\tDigit your ID number: ').strip()
    Data['password'] = input('\n\tDigit your password: ').strip()
    
    with open('User.csv', 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        accounts = []

        for row in reader:
            if len(Data['user']) < 4:
                break
            if row['User ID'].strip() == Data['user']:
                if row['Password'].strip() != Data['password']:
                    print("!Wrong Password.")
                    return False

                account_info = {
                    'user': row['User ID'].strip(),
                    'name': row['First Name'].strip(),
                    'lastName': row['Last Name'].strip(),
                    'email': row['Email Address'].strip(),
                    'account_type': row['Account Type'].strip(),
                    'account_number': row['Account Number'].strip(),
                    'balance': row['Balance'].strip(),
                    'password': row['Password'].strip()
                }
                accounts.append(account_info)

    if accounts:
        print("\nSelect the account you want to manage: ")
        for idx, account in enumerate(accounts, start=1):
            if isinstance(account, dict):
                print(f"\t{idx}. Account Type: {account['account_type']}, Account Number: {account['account_number']}, Balance: {account['balance']}")

        account_choice = int(input('\nEnter the number of the account: ')) - 1
        if 0<= account_choice < len(accounts):
            selected_account = accounts[account_choice]
            Data['user'] = selected_account['user']
            Data['account_type'] = selected_account['account_type']
            Data['account_number'] = selected_account['account_number']
            Data['name'] = selected_account['name']
            Data['lastName'] = selected_account['lastName']
            Data['email'] = selected_account['email']
            Data['balance'] = selected_account['balance']
            Data['password'] = selected_account['password']
        return True
    else:
        print("User not found.")
        return False

def delete():
    
    deleteAccount()
    deleteAccountSQL()

def deleteAccount():
    global Data
    with open('User.csv', 'r', newline='') as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)
        rows = [row for row in reader]
    rows_filtered = [
        row for row in rows
        if not (row[0] == Data['user'] and 
                row[4] == Data['account_type'] and
                row[5] == Data['account_number'] and 
                row[7] == Data['password'])
    ]

    with open('User.csv', 'w', newline='') as file:
        writer = csv.writer(file,delimiter=';')
        writer.writerow(headers)
        writer.writerows(rows_filtered)
        

def deleteAccountSQL():
    
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    global Data
    user_id = Data['user']
    account_type = Data['account_type']

    try:
        # Seleccionar el account_id
        cur.execute('''SELECT account_id FROM Accounts WHERE user_id = ? AND account_type = ?''', (user_id, account_type))
        account_id = cur.fetchone()[0]

        if account_id:
            print("The account_id selected is :", account_id)

            cur.execute('''DELETE FROM Accounts WHERE account_id = ?''', (account_id,))
            print("Account was deleted successfully ")
        else:
            print("No account was found with the user_id y account_type typed.")
            
                
        conn.commit()
    except sqlite3.Error as e:
                print("An error occurred while accessing the database:", e)
    finally:
                
                conn.close()

def deleteUser():
    global Data

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    user_id = Data['user']
    password = Data['password']

    cur.execute('''SELECT email FROM users WHERE user_id = ? AND password = ?''', (user_id,password, ))
    email = cur.fetchone()[0]

    if email:
        print("The User ",user_id," with the email ", email, "does not have account in our system")
        cur.execute('''DELETE FROM users Where user_id = ?''',(user_id, ))
    else: 
        print('No account was found')
    
    conn.commit()
    conn.close()
def countUsers():
    try:
        with open('User.csv', 'r') as file:
            reader = csv.reader(file,delimiter=';')
            lines = list(reader)

        existing_user_id = None

        for line in lines: 
            user_id, name, email = line[0], line[1], line[3] 
            if name.strip() == Data['name'] and email.strip() == Data['email']:
                existing_user_id = int(user_id.strip())
                break
        if existing_user_id is not None:
            count['count'] = existing_user_id
        else:
            if lines:
                last_user_id = int(lines[-1][0].strip())
                count['count'] = last_user_id + 1
            else:
                count['count'] = 1

    except FileNotFoundError:
        count['count'] = 1
    except ValueError as e:
        print(f"Error al convertir el ID de usuario a entero: {e}")
        count['count'] = 1

def loadToSQL():

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        password TEXT
    );
    CREATE TABLE IF NOT EXISTS Accounts (
        account_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        account_type TEXT,
        account_number TEXT,
        balance REAL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )                  
    ''')
    conn.commit()
    conn . close()

def addUserToSQL():

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    
    cur.execute('''
    INSERT INTO users (user_id, first_name, last_name, email, password)
    VALUES (?, ?, ?, ?, ?)
    ''', (Data['user'], Data['name'], Data['lastName'], Data['email'], Data['password']))
    
    cur.execute('''
    SELECT user_id FROM Users WHERE email = ?''', (Data['email'], ))
    user_id = cur.fetchone()[0]
    balance = float(Data['balance'].strip().replace('$','').replace(',',''))

    cur.execute('''
    INSERT INTO Accounts (user_id,account_type, account_number, balance)
    VALUES (?,?,?,?)''', (user_id,Data['account_type'], Data['account_number'], balance))
    conn.commit()
    conn.close()

def updateBalanceSQL():
    conn = sqlite3.connect('users.db')  
    cur = conn.cursor()

    cur.execute('''
    UPDATE users
    SET balance = ?
    WHERE users_id = ?
    ''', (float(Data['balance'].strip('$')), Data['user']))
    conn.commit()
    conn.close() 

def updateBalanceCSV():
    global Data
    user_id = Data['user']
    account_type = Data['account_type']
    account_number = Data['account_number']
    balance = float(Data['balance'])
    formatted_balance = f"${balance:.2f}"
    new_balance = formatted_balance

    with open('User.csv', 'r', newline='') as file:
        reader = csv.reader(file,delimiter=';')
        rows = list(reader)

    user_found = False

    for row in rows: 
        if row[5].strip() == account_number and row[0].strip() == user_id and row[4].strip() == account_type:
            row[6] = new_balance
            user_found = True
            break
    
    with open('User.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(rows)

    if user_found:
        print(f"User ID {user_id} and Account Type {account_type} updated successfully.")
    else:
        print(f"User ID {user_id} with Account Type {account_type} not found.")


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

def sortedUsers():

    with open('User.csv', 'r')as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)
        rows = list(reader)

    rows_sorted = sorted(rows,key=lambda x: int(x[0]))
    
    with open('User.csv', 'w', newline='')as file:
        writer = csv.writer(file,delimiter=';')
        writer.writerow(headers)
        writer.writerows(rows_sorted)

def logOut():
    quit()

print(menu())
