import os
import time
import msvcrt
import sqlite3
import webbrowser

from datetime import datetime

db_file = "current_inventory.db"

def console_clear():
    os.system('cls' if os.name == 'nt' else 'clear')

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def db_init():
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

        # Print header
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
    console_clear()
    
    product_quantities = {}

    # Gather product codes and quantities from the user directly within the function
    while True:
        code = input("Enter product code or EAN (or press Enter to finish, type 'custom' to add a custom product): ").strip()
        if not code:
            break

        if code == 'custom':
            custom_name = input("Enter custom product name: ")
            while True:
                try:
                    quantity = float(input(f"Enter quantity (F.PK) for {custom_name}: "))
                    break
                except ValueError:
                    print("Invalid quantity. Please enter a valid number.")
            product_quantities[custom_name] = quantity
        else:
            # Fetch product details from the database
            cursor.execute("SELECT product_name FROM products WHERE product_code=? OR ean=?", (code, code))
            result = cursor.fetchone()

            if result:
                product_name = result[0]
                while True:
                    try:
                        quantity = float(input(f"Enter quantity for {product_name}: "))
                        break
                    except ValueError:
                        print("Invalid quantity. Please enter a valid number.")
                product_quantities[product_name] = quantity
            else:
                print("Invalid product code or EAN. Please try again.")

    current_date = datetime.now().strftime("%d-%m-%Y")

    # Create a list of products with their locations
    products_with_locations = []
    for product_name, quantity in product_quantities.items():
        # Find the product code and location from the database
        cursor.execute("SELECT product_code FROM products WHERE product_name=?", (product_name,))
        result = cursor.fetchone()

        if result:
            product_code = result[0]
            location = "Unknown"  # Assuming no location field in DB, adjust if needed
            products_with_locations.append((product_name, quantity, location))

    # Sort products based on storage locations
    products_with_locations.sort(key=lambda item: item[2])  # Sort by location

    # Generate HTML content
    html_content = f'''
    <html>
    <head>
        <title>Lagerliste LVS</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; border: 1px solid black; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <img src="https://files.catbox.moe/x46dlm.png" alt="Company Logo" style="width:1250;">
        <p>Dato: {current_date}</p>
        <table>
            <tr>
                <th>Produktnavn</th>
                <th>Kvante (F.PK)</th>
                <th>Plassering</th>
            </tr>
    '''

    for product_name, quantity, location in products_with_locations:
        html_content += f'''
            <tr>
                <td>{product_name}</td>
                <td>{quantity}</td>
                <td>{location}</td>
            </tr>
        '''

    html_content += '''
        </table>
    </body>
    </html>
    '''

    # Save and open the HTML file
    html_file = "lagerliste.html"
    with open(html_file, "w") as file:
        file.write(html_content)

    print("HTML file created successfully. Opening it in your web browser...")

    # Get the absolute path of the file and open it in the browser
    absolute_path = os.path.abspath(html_file)
    webbrowser.open(f"file://{absolute_path}")

    pressAnyKeyForMenu()


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
    # add confirm
    console_clear()
    rp_pcode = input("Enter the product code or EAN of the product you want to delete:")

    if rp_pcode.isdigit():
        cursor.execute("SELECT product_name FROM products WHERE ean=?", (rp_pcode,))
        result = cursor.fetchone()
        
        if result:
            confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
            if confirmation_delete.lower() == "y":
                cursor.execute("DELETE FROM products WHERE ean=?", (rp_pcode,))
        else:
            print("Product not found.")
    
    elif rp_pcode.isalpha():
        cursor.execute("SELECT product_name FROM products WHERE product_code=?", (rp_pcode,))
        result = cursor.fetchone()

        if result:
            confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
            if confirmation_delete.lower() == "y":
                cursor.execute("DELETE FROM products WHERE product_code=?", (rp_pcode,))
                console_clear()
                print(f"{result[0]} was deleted")
                time.sleep(0.5)
                menu()
        else:
            print("Product not found.")
    
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
