import os
import time
import msvcrt
import sqlite3
import webbrowser

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
                        current_stock INTEGER,
                        location TEXT,
                        supplier TEXT,
                        status TEXT
                    )''')
    conn.commit()

def get_keypress():
    return msvcrt.getch().decode('utf-8')

def pressAnyKeyForMenu():
    print("Press any key to go back to the menu...")
    get_keypress()
    menu()

db_init()

def writeToDB(product_name, product_code, ean, current_stock, location, supplier, status):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Insert new product the database
    cursor.execute("INSERT INTO products (product_name, product_code, ean, current_stock, location, supplier, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (product_name, product_code, ean, current_stock, location, supplier, status))
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
    print("3. Update individual product stock")
    print("4. Update inventory")
    print("5. Enter new product into system")
    print("6: Edit products")
    print("7: Remove product from system")
    print("8: Settings/information")
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
        editProduct()
    elif choice == "7":
        removeProduct()
    elif choice == "8":
        settings()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        menu()


def viewStock():
    console_clear()
    cursor.execute("SELECT id, product_name, product_code, current_stock, location, status FROM products")
    results = cursor.fetchall()

    # header
    print(f"{'ID':<5} {'Product Name':<30} {'Product Code':<15} {'Current Stock':<15} {'Location':<15} {'Status':<5}")
    print("-" * 95)

    # print results
    for row in results:
        id, product_name, product_code, current_stock, location, status = row
        
        #status color
        if status.lower() == "active":
            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
        elif status.lower() == "inactive":
            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
        else:
            status_display = status

        print(f"{id:<5} {product_name:<30} {product_code:<15} {current_stock:<15} {location:<15} {status_display:<5}")
    
    print(" ")
    pressAnyKeyForMenu()

def generatePicklist(): #make it remove from stock, and add cancel functionality
    console_clear()
    
    product_quantities = {}

    while True:
        code = input("Enter product code or EAN (or press Enter to generate, type 'custom' to add a custom product, type 'exit' to quit): ").strip()
        if not code:
            break

        if code.lower() == "exit":
            menu()

        if code.lower() == 'custom':
            custom_name = input("Enter custom product name: ")
            while True:
                try:
                    quantity = float(input(f"Enter quantity (F.PK) for {custom_name}: "))
                    break
                except ValueError:
                    print("Invalid quantity. Please enter a valid number.")
            product_quantities[custom_name] = quantity
        else:
            # Fetch product details
            cursor.execute("SELECT product_name FROM products WHERE product_code=? OR ean=?", (code.upper(), code))
            result = cursor.fetchone()
            cursor.execute("SELECT current_stock FROM products WHERE product_code=? OR ean=?", (code.upper(), code))
            stock = cursor.fetchone()
            if result:
                product_name = result[0]
                while True:
                    try:
                        quantity = float(input(f"Enter quantity for {product_name} (Current inventory quantity: {stock[0]}): "))
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
        cursor.execute("SELECT product_code, location FROM products WHERE product_name=?", (product_name,))
        result = cursor.fetchone()  # Use fetchone to get a single result

    if result:
        product_code, location = result  # Unpack the tuple into product_code and location
        products_with_locations.append((product_name, quantity, location))
    else:
        print(f"Product {product_name} not found in the database.")


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

    removeFromDB_choice = input("Do you want to update the inventory stock for the products in the picklist? (Y/N)")

    if removeFromDB_choice.lower() == "y":
        print("WIP")



def updateStock():
    console_clear()
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
    print("New product (Type 'exit' to cancel):")
    print(" ")
    np_pname = input("Product name: ")
    if np_pname.lower() == "exit":
        menu()
    np_pcode = input("Product code: ")
    if np_pcode.lower() == "exit":
        menu()
    np_ean = input("Product EAN (Enter = no EAN): ")
    if np_ean.lower() == "exit":
        menu()
    np_currentstock = input("Current product stock: ")
    if np_currentstock.lower() == "exit":
        menu()
    np_location = input("Location (press enter for no location): ")
    if np_location.lower() == "exit":
        menu()
    np_supplier = input("Product supplier (press enter for no supplier): ")
    if np_supplier.lower() == "exit":
        menu()
    status = input("Product status (A = Active, I = Inactive. this can be further specified later): ")
    if status.lower() == "exit":
        menu()
    elif status.lower() == "a":
        np_status = "Active"
    elif status.lower() == "i":
        np_status = "Inactive"
    else:
        np_status = status

    writeToDB(np_pname, np_pcode, np_ean, np_currentstock, np_location, np_supplier, np_status)
    print(f"{np_pname} has been successfully added to StockFox")
    print(f"Stockfox entry: Name: {np_pname}, Code: {np_pcode}, EAN: {np_ean}, Stock: {np_currentstock}, Location: {np_location}, Supplier: {np_supplier}, Status: {np_status}")
    print(" ")
    pressAnyKeyForMenu()

def editProduct():
    console_clear()
    ep_pcode = input("Please input the product code for the product you want to edit (or press Enter to exit): ")
    danger = "drop"



    if ep_pcode.lower() == "sql":
        print(" ")
        print(bcolors.WARNING + "WARNING: Custom SQL commands can be very dangerous. Only do this if you know what you're doing!" + bcolors.ENDC)
        while True:    
            custom_sql = input("SQL command (type 'exit' to go back to menu): ")
            if custom_sql.lower() == "exit":
                menu()
            
            if danger in custom_sql.lower():
                danger_conf = input(f"Are you sure you want to run the SQL command '{custom_sql}'? (Y/N) ")
                if danger_conf.lower() != "y":
                    print("Command cancelled.")
                    continue
                    
            try:
                cursor.execute(custom_sql)
                result = cursor.fetchall()
                print(result)
            
            except:
                print("Invalid SQL query.")
        
        

    cursor.execute("SELECT * FROM products WHERE product_code=?", (ep_pcode.upper(),))
    result = cursor.fetchone()
    status = result[7]
    if result:
        if status.lower() == "active":
            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
        elif status.lower() == "inactive":
            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
        else:
            status_display = status
        print(" ")
        print(f"1. Product name: {result[1]}")
        print(f"2. Product code: {result[2]}")
        print(f"3. Product EAN: {result[3]}")
        print(f"4. Product location: {result[5]}") #stock is not displayed here, skipping [4]
        print(f"5. Product supplier: {result[6]}")
        print(f"6. Product status: {status_display}")
        print(" ")
        entryEdit = input("Enter which line you want to edit: ")
        if entryEdit == 1:
            ep_name = input("Please enter new product name: ")


def removeProduct():
    console_clear()
    print("Remove product:")
    print(" ")
    rp_pcode = input("Enter the product code or EAN of the product you want to delete (or press Enter to cancel): ")

    if rp_pcode == "":
        menu()

    #wipe db function:
    elif rp_pcode.lower() == "drop table":
        the_choice = input("Are you sure? This action can NOT be undone! (Y/N) ")
        if the_choice.lower() == "y":
            print(" ")
            the_second_choice = input("This will quite literally remove everything. are you SURE you want to do this? (Y/N) ")
            if the_second_choice.lower() == "y":
                print(" ")
                the_last_choice = input("To confirm, please write 'I am fully aware this will delete the database' ")
                if the_last_choice.lower() == "i am fully aware this will delete the database":
                    cursor.execute("DROP TABLE products")
                    print("Table dropped. This action requires a full restart of Stockfox. Please relaunch the program.")
                    conn.commit()
                    exit()

                else:
                    removeProduct()
            else:
                removeProduct()
        else:
            removeProduct()

    elif rp_pcode.isdigit():
        cursor.execute("SELECT product_name FROM products WHERE ean=?", (rp_pcode,))
        result = cursor.fetchone()
        
        if result:
            confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
            if confirmation_delete.lower() == "y":
                cursor.execute("DELETE FROM products WHERE ean=?", (rp_pcode,))
        else:
            print("Product not found.")
            time.sleep(0.5)
            removeProduct()
    
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
            time.sleep(0.5)
            removeProduct()
    
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
