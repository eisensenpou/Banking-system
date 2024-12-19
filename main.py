import bcrypt  # Install first by using 'pip install bcrypt'
import re
import random as r
import json

class Bank:
    def __init__(self, name, email, account_number, password, routing_number=123456789, balance=0):
        self.name = name
        self.email = email
        self.balance = balance
        self.account_number = account_number
        self.routing_number = routing_number
        self.password = password

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
        else:
            print("Insufficient funds")

    def check_balance(self):
        print("Balance: ", self.balance)

    def send_money(self, amount, recipient):
        if self.balance >= amount:
            self.balance -= amount
            recipient.balance += amount
        else:
            print("Insufficient balance")

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "account_number": self.account_number,
            "password": self.password,
            "routing_number": self.routing_number,
            "balance": self.balance
        }

database = {"customers": []}

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True
    return False

used_account_numbers = set()

def account_number_generator():
    while True:
        number = "".join(str(r.randint(0, 9)) for _ in range(10))  # Generate a 10-digit number
        if number not in used_account_numbers:  # Ensure uniqueness
            used_account_numbers.add(number)
            return number

def save_to_json(data):
    with open('database.json', 'w') as file:
        json.dump(data, file, indent=4)

def load_from_json():
    global database  # Ensure we're modifying the global `database` variable
    with open('database.json') as f:
        data = json.load(f)
        database = {"customers": []}

        # Convert dictionaries to Bank objects
        for customer_data in data.get("customers", []):
            customer = Bank(
                customer_data["name"],
                customer_data["email"],
                customer_data["account_number"],
                customer_data["password"],
                customer_data.get("routing_number", 123456789),
                customer_data.get("balance", 0)
            )
            database["customers"].append(customer)

def hash_password(plain_password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def registration():
    while True:
        name = input("Full Name: ")
        if not name:
            print("Full Name cannot be empty. Try again!")
            continue

        email = input("Email: ")
        if not validate_email(email):
            print("Invalid Email! Please try again.")
            continue
        elif email in [customer.email for customer in database["customers"]]:  # Change to check email in object format
            print("This email is already in use. Please try again.")
            continue

        while True:
            print("Please use special characters, numbers, and lower and upper case letters!")
            password = input("Password: ")
            if len(password) < 8:
                print("This password is too short. Please use at least 8 characters.")
                continue

            ver_password = input("Type the password again: ")
            if password != ver_password:
                print("Passwords don't match. Try again!")
                continue
            break
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        account_number = account_number_generator()

        customer = Bank(name, email, account_number, hashed_password)
        database["customers"].append(customer)  # Add the Bank object directly
        save_to_json(database)
        print(f"Registration successful! Your account number is: {account_number}")
        break

def login():
    email = input("Email: ")
    password = input("Password: ")

    # Search for the user in the database, which now holds Bank objects
    user = next((customer for customer in database["customers"] if customer.email == email), None)

    if user:
        if verify_password(password, user.password):  # Verify using bcrypt
            print("Login successful!")
            return user
        else:
            print("Invalid password.")
    else:
        print("User not found.")

def action_choice(user):
    choice = input("What do you want to do?\n(1)Check Balance\n(2)Send money\n")
    if choice == "1":
        user.check_balance()
    elif choice == "2":
        amount = float(input("Please enter the amount: "))
        recipient_account = input("Enter the recipient's account number: ")

        # Find the recipient Bank object by account number
        recipient = next((cust for cust in database["customers"] if cust.account_number == recipient_account), None)

        if recipient:
            user.send_money(amount, recipient)
        else:
            print("Recipient not found.")
    else:
        return None

def main():
    print("Welcome to the X banking.")
    load_from_json()
    while True:
        login_check = input("Do you want to (1)login or (2)register? ")

        if login_check == "1":
            user = login()  # Assuming login() returns a user if successful, None otherwise
            if user:
                action_choice(user)  # Perform actions for logged-in user
            else:
                print("Login failed. Please try again.")
        elif login_check == "2":
            registration()  # Perform registration and then return to main
        else:
            decision = input("Incorrect input. Do you want to exit? Y/N: ")
            if decision.lower() == "y":
                exit()
            else:
                continue


main()
