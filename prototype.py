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

def menu():
    console_clear()
    print("   _____  _                 _     ______          ")
    print("  / ____|| |               | |   |  ____|         ")
    print(" | (___  | |_   ___    ___ | | __| |__  ___ __  __")
    print("  \___ \ | __| / _ \  / __|| |/ /|  __|/ _ \\ \/ /")
    print("  ____) || |_ | (_) || (__ |   < | |  | (_) |>  < ")
    print(" |_____/  \__| \___/  \___||_|\_\|_|   \___//_/\_\ ")
    print(" ")
    print("1. View current stock")
    print("2. Generate picklist")
    print("3. Update product stock")
    print("4. Add new stock to system")
    print("5. Enter new product into system")
    print("6: Remove product from system")
    print("7: Settings/information")
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
        addStock()
    elif choice == "5":
        newProduct()
    elif choice == "6":
        removeProduct()
    elif choice == "7":
        settings()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        menu()


def viewStock():
        console_clear()
        cursor.execute("SELECT id, product_name, product_code, current_stock FROM products")
        results = cursor.fetchall()

        # Print a header for the table
        print(f"{'ID':<5} {'Product Name':<30} {'Product Code':<15} {'Current Stock':<15}")
        print("-" * 70)

        # Iterate through the results and print each product in a pretty format
        for row in results:
            id, product_name, product_code, current_stock = row
            print(f"{id:<5} {product_name:<30} {product_code:<15} {current_stock:<15}")
        
        print(" ")
        pressAnyKeyForMenu()


#picklist

def generatePicklist():
    print("WIP")

def updateStock():
    print("Update stock:")
    print(" ")
    while True:
        us_pcode = input("Enter product code or scan barcode (or press Enter to save/exit): ")
        if us_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (us_pcode,))
            result = cursor.fetchone() 
            if result:
                cursor.execute("SELECT current_stock FROM products WHERE ean=?", (us_pcode,))
                current_quantity = cursor.fetchone() 
                product_name = result[0]
                us_quantity = input(f"Enter quantity of {product_name} (current quantity: {current_quantity}): ")
                cursor.execute("UPDATE products SET current_stock = ? WHERE ean=?", 
                               (us_quantity, us_pcode))
            else:
                print("Product not found.")
                time.sleep(0.5)
                updateStock()

        elif us_pcode.isalpha():
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (us_pcode,))
            result = cursor.fetchone() 
            if result:
                cursor.execute("SELECT current_stock FROM products WHERE product_code=?", (us_pcode,))
                current_quantity = cursor.fetchone() 
                product_name = result[0]
                us_quantity = input(f"Enter quantity of {product_name} (current quantity: {current_quantity}): ")
                cursor.execute("UPDATE products SET current_stock = ? WHERE product_code=?", 
                               (us_quantity, us_pcode))
            else:
                print("Product not found.")
                time.sleep(0.5)
                updateStock()

        else:
            menu()
            

            


def addStock():
    console_clear()
    print("Add stock:")
    print(" ")
    while True: 
        as_pcode = input("Enter product code or scan barcode (or press Enter to save/exit): ")
        if as_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (as_pcode,))
            result = cursor.fetchone() 
            if result:
                product_name = result[0]
                as_quantity = input(f"Enter quantity of {product_name} to be added to inventory: ")
                cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE ean=?", 
                               (as_quantity, as_pcode))
            else:
                print("Product not found.")
        elif as_pcode.isalpha():
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (as_pcode,))
            result = cursor.fetchone()
            if result:
                product_name = result[0]
                as_quantity = input(f"Enter quantity of {product_name} to be added to inventory: ")
                cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE product_code=?", 
                               (as_quantity, as_pcode))
            else:
                print("Product not found.")
                time.sleep(0.5)
                addStock()
        else:
            menu()
            
    




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
    rp_pcode = input("Enter the product code or EAN of the product you want to delete:")

    if rp_pcode.isdigit():
        cursor.execute("SELECT product_name FROM products WHERE ean=?",
                        (rp_pcode,))
        result = cursor.fetchone()
        confirmation_delete = input(f"Are you sure you want to delete {result}? (Y/N)")
        if confirmation_delete == "y" or confirmation_delete == "Y":
            cursor.execute("DELETE FROM products WHERE ean=?",
                   (rp_pcode))
        else:
            menu()

    elif rp_pcode.isalpha():
        cursor.execute("SELECT product_name FROM products WHERE product_code=?",
                        (rp_pcode,))
        result = cursor.fetchone()
        confirmation_delete = input(f"Are you sure you want to delete {result}? (Y/N)")
        if confirmation_delete == "y" or confirmation_delete == "Y":
            cursor.execute("DELETE FROM products WHERE product_code=?",
                   (rp_pcode))
        else:
            menu()
        
    
    else:
        menu()
        
    conn.commit()

def settings():
    console_clear()
    print("---------- StockFox ----------")
    print("2024 © Lien Vending Solutions")
    print("Version Alpha")
    print("Made in Norway ♥")
    print("")
    print("Support: stockfox@lienvending.solutions")
    print(" ")
    pressAnyKeyForMenu()
menu()
