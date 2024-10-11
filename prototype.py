import os
import time
import msvcrt
import sqlite3

db_file = "current_inventory.db"


def console_clear():
    os.system('cls' if os.name == 'nt' else 'clear')

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def db_init():
    # Connect to SQLite and create a table if it doesn't exist
    # Create table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        product_code TEXT NOT NULL,
                        ean INTEGER,
                        current_stock INTEGER
                    )''')
    conn.commit()
    conn.close()

def get_keypress():
    return msvcrt.getch().decode('utf-8')

def pressAnyKeyForMenu():
    print("Press any key to go back to the menu...")
    get_keypress()
    menu()

db_init()

def writeToDB(product_name, product_code, ean, current_stock):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Insert a new product into the database
    cursor.execute("INSERT INTO products (product_name, product_code, ean, current_stock) VALUES (?, ?, ?, ?)", 
                   (product_name, product_code, ean, current_stock))
    conn.commit()
    conn.close()


def menu():
    console_clear()
    print("   _____  _                _     ______          ")
    print("  / ____|| |              | |   |  ____|         ")
    print(" | (___  | |_  ___    ___ | | __| |__  ___ __  __")
    print("  \___ \ | __|/ _ \  / __|| |/ /|  __|/ _ \\ \/ /")
    print("  ____) || |_| (_) || (__ |   < | |  | (_) |>  < ")
    print(" |_____/  \__|\___/  \___||_|\_\|_|   \___//_/\_\ ")
    print(" ")
    print("1. View current stock")
    print("2. Generate picklist")
    print("3. Update product stock")
    print("4. Enter new product into system")
    print("5: Remove product from system")
    print("6: Settings/information")
    choice = get_keypress()
    run(choice)

def run(choice):
    if choice == "1":
        viewStock()
    elif choice == "2":
        generatePicklist()
    elif choice == "3":
        updateStock()
    elif choice == "4":
        newProduct()
    elif choice == "5":
        removeProduct()
    elif choice == "6":
        settings()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        menu()


def viewStock():
    #todo  
    print("WIP")  

def generatePicklist():
    #todo
    print("WIP")  


def updateStock():
    #todo
    print("WIP")  

def newProduct():
    console_clear()
    np_pname = input("Product name: ")
    np_pcode = input("Product code: ")
    np_ean = input("Product EAN (0 = no EAN): ")
    np_currentstock = input("Current product stock: ")
    writeToDB(np_pname, np_pcode, np_ean, np_currentstock)
    print(f"{np_pname} has been successfully added to StockFox")
    print(f"Stockfox entry: Name: {np_pname}, Code: {np_pcode}, EAN: {np_ean}, Stock: {np_currentstock}")
    print(" ")
    pressAnyKeyForMenu()

def removeProduct():

    #add confirm
    console_clear()
    product_delete = input("Enter the product code or EAN of the product you want to delete:")

    if product_delete.isdigit():
        cursor.execute("DELETE FROM products WHERE ean=?",
                   (product_delete))
    else:

        cursor.execute("DELETE FROM products WHERE product_name=?"
                       (product_delete))
        
    conn.commit()

def settings():
    console_clear()
    print("---------- StockFox ----------")
    print("2024 © Lien Vending Solutions")
    print("Version Alpha")
    print("Made in Norway ♥")
    print("")
    pressAnyKeyForMenu()
menu()
