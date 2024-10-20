import os
import time
import msvcrt
import sqlite3
import webbrowser
from barcode.writer import ImageWriter
from PIL import Image
import numpy as np
import csv
from datetime import datetime


def generate_barcode_to_terminal(code):
    code = str(code)  # Convert input to string if it's not already
    
    # Encoding for each digit (0-9)
    encoding = {
        '0': '█  █    ',
        '1': '█   █   ',
        '2': '█   █  █',
        '3': '█   █ █ ',
        '4': '█    ██ ',
        '5': '█    █ █',
        '6': '█    █  █',
        '7': '  █ █   █',
        '8': '  █  █  █',
        '9': '  █   █ █'
    }

    # Start with the left guard pattern (as normal)
    barcode_str = '█'  # Start guard bar

    # Loop through each digit in the input code and translate it
    for digit in code:
        if digit in encoding:
            barcode_str += encoding[digit]
        else:
            raise ValueError(f"Invalid character '{digit}' in the input. Only digits 0-9 are allowed.")

    # End with the right guard pattern
    barcode_str += '█'  # End guard bar

    # Print the barcode multiple times without inverting
    for i in range(8):  # Adjust the range to display multiple lines if needed
        print(barcode_str)


def addEanToProduct():
    while True:
        AETP_pcode = input("Input product code (or press Enter to exit): ")
        if AETP_pcode == "":
            menu()
            break
        
        AETP_ean = input("Add EAN: ")
        
        try:
            cursor.execute("UPDATE products SET ean=? WHERE product_code=?", (AETP_ean, AETP_pcode))
            conn.commit()
            
            cursor.execute("SELECT product_name, ean FROM products WHERE product_code=?", (AETP_pcode,))
            check = cursor.fetchone() 
            
            if check:
                print(f"'{check[0]}' updated EAN to: {check[1]}")
            else:
                print("Product not found.")
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(0.5)


def backup_products_to_csv():
    # Set the database name
    db_name = 'current_inventory.db'
    
    # Get the current working directory
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Get the current date and time for the timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_name = f"export_{timestamp}.csv"

    # Build the full path for the database and the CSV file
    db_path = os.path.join(current_directory, db_name)
    csv_file_path = os.path.join(current_directory, csv_file_name)

    # Execute a query to fetch all records from the products table
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()

    # Get the column names
    column_names = [description[0] for description in cursor.description]

    # Write to a CSV file
    with open(csv_file_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)  # Write the header
        writer.writerows(rows)  # Write all rows

    # Close the connection
    print(f"Backup completed: {csv_file_path}")
    time.sleep(1)

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
                        status TEXT,
                        unit_price TEXT,
                        sale_price TEXT

                    )''')
    conn.commit()

def get_keypress():
    return msvcrt.getch().decode('utf-8')

def pressAnyKeyForMenu():
    print("Press any key to go back to the menu...")
    get_keypress()
    menu()

db_init()

def writeToDB(product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Insert new product the database
    cursor.execute("INSERT INTO products (product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   (product_name, product_code.strip(), ean.strip(), current_stock, location, supplier, status, unit_price, sale_price))
    conn.commit()

def menu():
    console_clear()
    print("   _____  _                 _     ______          ")
    print("  / ____|| |               | |   |  ____|         ")
    print(" | (___  | |_   ___    ___ | | __| |__  ___ __  __")
    print("  \___ \ | __| / _ \  / __|| |/ /|  __|/ _ \\ \/ /")
    print("  ____) || |_ | (_) || (__ |   < | |  | (_) |>  < ")
    print(" |_____/  \__| \___/  \___||_|\_\|_|   \___//_/\_\ ")
    print("")
    print("1. View current stock")
    print("2. Generate picklist")
    print("3. Update individual product stock")
    print("4. Update/add inventory from new shipment")
    print("5. Insert new product into system")
    print("6: Edit products")
    print("7: View product details")
    print("8: Remove product from system")
    print("9: Settings/information")
    print("")
    print("0: Quit StockFox")
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
        console_clear()
        viewProductDetails()
    elif choice == "8":
        removeProduct()
    elif choice == "9":
        settings()
    elif choice == "0":
        print("Are you sure you want to quit? (Y/N): ")
        exit_confirm = get_keypress()
        if exit_confirm.lower() == "y":
            conn.commit()
            while True:
                exit()
        else:
            menu()
    else:
        print("Invalid choice")
        time.sleep(0.5)
        menu()


def viewStock():
    console_clear()
    cursor.execute("SELECT product_name, product_code, current_stock, location, status, unit_price FROM products")
    results = cursor.fetchall()

    # Sort results: first by status (active first), then by location, then by stock (lowest first)
    results.sort(key=lambda row: (row[4].lower() != "active", row[3].lower(), row[2]))  # row[4] is status, row[3] is location, row[2] is current_stock
    conn.commit()

    # header
    print(f"{'Product Name':<30} {'Product Code':<15} {'Current Stock':<15} {'Location':<15} {'Status':<15} {'Stock Value':>10}")
    print("-" * 115)

    total_stock_value = 0
    
    # print results
    for row in results:
        product_name, product_code, current_stock, location, status, unit_price = row
        
        # Check for low stock
        low_stock_warning = ""
        if current_stock < 10:
            low_stock_warning = " (low stock!)"
        if status.lower() == "inactive":
            low_stock_warning = ""

        current_stock_value = current_stock

        current_stock = str(current_stock) + low_stock_warning

        # status color
        if status.lower() == "active":
            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
        elif status.lower() == "inactive":
            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
        else:
            status_display = status

        stock_value = round(float(current_stock_value) * float(unit_price), 2)  # round stock value to 2 decimal places
        total_stock_value = round(total_stock_value + stock_value, 2)  # round total stock value to 2 decimal places

        print(f"{product_name:<30} {product_code:<15} {current_stock:<15} {location:<15} {status_display:<24} {stock_value:<15}")
    
    print("")
    print(f"Total stock value: {total_stock_value}")
    print(" ")
    pressAnyKeyForMenu()

def generatePicklist():  # make it remove from stock, and add cancel functionality
    console_clear()
    
    product_quantities = {}

    while True:
        code = input("Enter product code or EAN (or press Enter to generate, type 'custom' to add custom product, type 'exit' to quit): ").strip()
        
        # check for exit condition
        if code.lower() == "exit":
            if not product_quantities:  # Check if no products have been added
                menu()
            else:
                # If products were added, ask for confirmation
                confirmation = input("You have unsaved products in your picklist. Are you sure you want to exit? (Y/N): ").strip().lower()
                if confirmation.lower() == "y":
                    menu()

        if code == "":
            break

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
            
            if result and stock:  # Ensure that both product and stock are found
                product_name = result[0]
                while True:
                    try:
                        quantity = float(input(f"Enter quantity for {product_name} (Current inventory quantity: {stock[0]}): "))
                        if quantity > stock[0]:
                            print("Quantity exceeds current stock. Please enter a valid quantity.")
                        else:
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

    removeFromDB_choice = input("Do you want to update the inventory stock for the products in the picklist? (Y/N): ")

    if removeFromDB_choice.lower() == "y":
        # Update the inventory in the database
        for product_name, quantity in product_quantities.items():
            # Fetch the current stock for the product
            cursor.execute("SELECT current_stock FROM products WHERE product_name=?", (product_name,))
            current_stock = cursor.fetchone()

            if current_stock and current_stock[0] >= quantity:  # Ensure there is enough stock
                new_stock = current_stock[0] - quantity
                # Update the database with the new stock
                cursor.execute("UPDATE products SET current_stock=? WHERE product_name=?", (new_stock, product_name))
                print(f"Updated {product_name}: New stock is {new_stock}.")
                pressAnyKeyForMenu()
            else:
                print(f"Not enough stock for {product_name}. Current stock is {current_stock[0] if current_stock else 0}.")
                pressAnyKeyForMenu()

        conn.commit()
        print("Inventory updated successfully.")
        time.sleep(1)
        menu()
    else:
        print("Inventory was not updated")
        time.sleep(1)
        menu()


def updateStock():
    console_clear()
    print("Update stock:")
    print("")
    while True:
        us_pcode = input("Enter product code or EAN (or press Enter to save/exit): ")
        if us_pcode == "":
            menu()
        elif us_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (us_pcode,))
            result = cursor.fetchone() 
            if result:
                cursor.execute("SELECT current_stock FROM products WHERE ean=?", (us_pcode,))
                current_quantity = cursor.fetchone() 
                product_name = result[0]
                us_quantity = input(f"Enter quantity of {product_name} (current quantity: {current_quantity[0]}): ")
                cursor.execute("UPDATE products SET current_stock = ? WHERE ean=?", 
                               (us_quantity, us_pcode))
                cursor.execute("SELECT current_stock FROM products WHERE ean=?", (us_pcode,))
                conn.commit()
                updatedQuantity = cursor.fetchone()
                if updatedQuantity:
                    print(f"{product_name} quantity is now: {updatedQuantity[0]}")
                else:
                    print(bcolors.WARNING + "WARNING: There seems to be an issue with the DB. Please double check quantity." + bcolors.ENDC)
            else:
                print("Product not found.")
                time.sleep(0.5)
                updateStock()

        else:
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (us_pcode,))
            result = cursor.fetchone() 
            if result:
                cursor.execute("SELECT current_stock FROM products WHERE product_code=?", (us_pcode,))
                current_quantity = cursor.fetchone() 
                product_name = result[0]
                us_quantity = input(f"Enter quantity of {product_name} (current quantity: {current_quantity[0]}): ")
                cursor.execute("UPDATE products SET current_stock = ? WHERE product_code=?", 
                (us_quantity, us_pcode))
                cursor.execute("SELECT current_stock FROM products WHERE product_code=?", (us_pcode,))
                updatedQuantity = cursor.fetchone()
                if updatedQuantity:
                    print(f"{product_name} quantity is now: {updatedQuantity[0]}")
                else:
                    print(bcolors.WARNING + "WARNING: There seems to be an issue with the DB. Please double check quantity." + bcolors.ENDC)

            else:
                print("Product not found.")
                time.sleep(0.5)
                updateStock()

            

            


def addStock():
    console_clear()
    print("Add stock:")
    print("")
    while True: 
        as_pcode = input("Enter product code or scan barcode (or press Enter to save/exit): ")
        if as_pcode == "":
            menu()
        elif as_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (as_pcode,))
            result = cursor.fetchone() 
            if result:
                product_name = result[0]
                as_quantity = input(f"Enter quantity of {product_name} to be added to inventory: ")
                cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE ean=?", 
                               (as_quantity, as_pcode))
            else:
                print("Product not found.")
                time.sleep(0.5)
                addStock()
        else:
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (as_pcode,))
            result = cursor.fetchone()
            if result:
                product_name = result[0]
                as_quantity = input(f"Enter quantity of {product_name} to be added to inventory: ")
                cursor.execute("UPDATE products SET current_stock = current_stock + ? WHERE product_code=?", 
                               (as_quantity, as_pcode))
                conn.commit()
            else:
                print("Product not found.")
                time.sleep(0.5)
                addStock()


def newProduct():
    console_clear()
    print("New product (Type 'exit' to cancel):")
    print("")
    np_pname = input("Product name: ")
    if np_pname.lower() == "exit":
        menu()
    np_pcode = input("Product code: ")
    if np_pcode.lower() == "exit":
        menu()
    elif not np_pcode.isalpha():
        print("Invalid charater (A-Z only)")
        time.sleep(0.5)
        newProduct()
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
    np_unit_price = input("Unit price (from supplier): ")
    if np_unit_price.lower() == "exit":
        menu()
    np_sale_price = input("Sale price: ")
    if np_sale_price.lower() == "exit":
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
    cursor.execute("SELECT * FROM products WHERE product_code=?", (np_pcode,))
    check = cursor.fetchall
    if check:
        print(f"Error: Product with product code {np_pcode} already exists")
        time.sleep(0.8)
        newProduct()
    else:
        writeToDB(np_pname, np_pcode, np_ean, np_currentstock, np_location, np_supplier, np_status, np_unit_price, np_sale_price)
        print(f"{np_pname} has been successfully added to StockFox")
        print("")
        print("Stockfox entry:")
        print(f"Name: {np_pname}, Code: {np_pcode}, EAN: {np_ean}, Stock: {np_currentstock}, Location: {np_location}")
        print(f"Supplier: {np_supplier}, Unit Price: {np_unit_price}, Sale Price: {np_sale_price} Status: {np_status}")
        print("")
        pressAnyKeyForMenu()

def editProduct():
    while True:
        try:  
            console_clear()
            ep_pcode = input("Please input the product code or EAN for the product you want to edit (or press Enter to exit): ")

            danger = "drop" #more flags can be added if required

            if ep_pcode == "":
                menu()

            if ep_pcode.lower() == "sql":
                print("")
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

            elif ep_pcode.lower() == "add ean":
                addEanToProduct()
                
            elif ep_pcode.lower() == "export" or ep_pcode.lower() == "export db" or ep_pcode.lower() == "backup":
                backup_products_to_csv()

            elif ep_pcode == "":
                menu()
            
            elif ep_pcode.isdigit():
                cursor.execute("SELECT * FROM products WHERE ean=?", (ep_pcode.upper(),))
                result = cursor.fetchone()
                status = result[7]
                if result:
                    if status.lower() == "active":
                        status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                    elif status.lower() == "inactive":
                        status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                    else:
                        status_display = status
                    print("")
                    print(f"1. Product name: {result[1]}")
                    print(f"2. Product code: {result[2]}")
                    print(f"3. Product EAN: {result[3]}")
                    print(f"4. Product location: {result[5]}") #stock is not displayed here, skipping [4]
                    print(f"5. Product supplier: {result[6]}")
                    print(f"6. Product status: {status_display}")
                    print("")
                    while True:
                        try: 
                            entryEdit = int(input("Enter which line you want to edit (or '0' to exit): "))
                            break

                        except ValueError:
                            print("Please input a number")
                            continue

                    if entryEdit == 0:
                        editProduct()

                    if entryEdit == 1:
                        new_name = input(f"Please enter new product name (current: {result[1]}): ")
                        cursor.execute("UPDATE products SET product_name=? WHERE ean=?", (new_name, ep_pcode.upper()))
                        conn.commit()
                        
                        print(f"Product name changed to {new_name} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 2:
                        new_pcode = input(f"Please enter new product code (Current: {result[2]}): ")
                        cursor.execute("UPDATE products SET product_code=? WHERE ean=?", (new_pcode, ep_pcode.upper()))
                        conn.commit() 
                        print(f"Product code changed to {new_pcode} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 3:
                        new_ean = input(f"Please enter new product EAN (Current: {result[3]}): ")
                        cursor.execute("UPDATE products SET ean=? WHERE ean=?", (new_ean, ep_pcode.upper()))
                        conn.commit() 
                        conn.commit()
                        print(f"Product EAN changed to {new_ean} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 4:
                        new_location = input(f"Please enter new product location (Current: {result[5]}): ")
                        cursor.execute("UPDATE products SET location=? WHERE ean=?", (new_location, ep_pcode.upper()))
                        conn.commit()
                        print(f"Product location changed to {new_location} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 5:
                        new_supplier = input(f"Please enter new product supplier (Current: {result[6]}): ")
                        cursor.execute("UPDATE products SET supplier=? WHERE ean=?", (new_supplier, ep_pcode.upper()))
                        conn.commit()
                        conn.commit()
                        print(f"Product supplier changed to {new_supplier} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 6:
                        ep_status = input(f"Please enter new product EAN (Current: {status_display} | A = Active, I = Inactive or type custom status): ")
                        if ep_status.lower() == "a":
                            new_status = "Active"
                        elif ep_status.lower() == "i":
                            new_status = "Inactive"
                        else:
                            new_status = ep_status
                        cursor.execute("UPDATE products SET status=? WHERE ean=?", (new_status, ep_pcode.upper()))
                        conn.commit()
                        if new_status.lower() == "active":
                            status_display_confirmation = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                        elif new_status.lower() == "inactive":
                            status_display_confirmation = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                        else:
                            status_display_confirmation = new_status
                        print(f"Product status changed to {status_display_confirmation} successfully")
                        time.sleep(1)
                        editProduct()

            else:
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
                    print("")
                    print(f"1. Product name: {result[1]}")
                    print(f"2. Product code: {result[2]}")
                    print(f"3. Product EAN: {result[3]}")
                    print(f"4. Product location: {result[5]}") #stock is not displayed here, skipping [4]
                    print(f"5. Product supplier: {result[6]}")
                    print(f"6. Product status: {status_display}")
                    print("")
                    while True:
                        try: 
                            entryEdit = int(input("Enter which line you want to edit (or '0' to exit): "))
                            break

                        except ValueError:
                            print("Please input a number")
                            continue

                    if entryEdit == 0:
                        editProduct()

                    if entryEdit == 1:
                        new_name = input(f"Please enter new product name (current: {result[1]}): ")
                        cursor.execute("UPDATE products SET product_name=? WHERE product_code=?", (new_name, ep_pcode.upper()))
                        conn.commit()
                        print(f"Product name changed to {new_name} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 2:
                        new_pcode = input(f"Please enter new product code (Current: {result[2]}): ")
                        cursor.execute("UPDATE products SET product_code=? WHERE product_code=?", (new_pcode, ep_pcode.upper()))
                        conn.commit()
                        print(f"Product code changed to {new_pcode} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 3:
                        new_ean = input(f"Please enter new product EAN (Current: {result[3]}): ")
                        cursor.execute("UPDATE products SET ean=? WHERE product_code=?", (new_ean, ep_pcode.upper()))
                        conn.commit()
                        print(f"Product EAN changed to {new_ean} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 4:
                        new_location = input(f"Please enter new product location (Current: {result[5]}): ")
                        cursor.execute("UPDATE products SET location=? WHERE product_code=?", (new_location, ep_pcode.upper()))
                        conn.commit()
                        print(f"Product location changed to {new_location} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 5:
                        new_supplier = input(f"Please enter new product supplier (Current: {result[6]}): ")
                        cursor.execute("UPDATE products SET supplier=? WHERE product_code=?", (new_supplier, ep_pcode.upper()))
                        conn.commit()
                        print(f"Product supplier changed to {new_supplier} successfully")
                        time.sleep(1)
                        editProduct()
                    elif entryEdit == 6:
                        ep_status = input(f"Please enter new product EAN (Current: {status_display} | A = Active, I = Inactive or type custom status): ")
                        if ep_status.lower() == "a":
                            new_status = "Active"
                        elif ep_status.lower() == "i":
                            new_status = "Inactive"
                        else:
                            new_status = ep_status
                        cursor.execute("UPDATE products SET status=? WHERE product_code=?", (new_status, ep_pcode.upper()))
                        if new_status.lower() == "active":
                            status_display_confirmation = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                        elif new_status.lower() == "inactive":
                            status_display_confirmation = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                        else:
                            status_display_confirmation = new_status
                        print(f"Product status changed to {status_display_confirmation} successfully")
                        time.sleep(1)
                        editProduct()
        except:
            print("Invalid product, try again")

def viewProductDetails():
    print("View product details:")
    print("")
    while True:
        VPD_code = input("Enter product code or EAN (or press Enter to exit): ")
        try:
            if VPD_code == "":
                menu()

            elif VPD_code.isdigit():
                cursor.execute("SELECT * FROM products WHERE ean=?", (VPD_code,))
                result = cursor.fetchall()
                
                if result:
                    if len(result[0]) > 7:  # Ensure there are enough columns in the result
                        status = result[0][7]  # Assuming status is at index 7
                        if status.lower() == "active":
                            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                        elif status.lower() == "inactive":
                            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                        else:
                            status_display = status

                        # Accessing product details safely
                        print("")
                        print(f"Product name: {result[0][1]}")  # Access first product
                        print(f"Product code: {result[0][2]}")
                        print(f"Product EAN: {result[0][3]}")
                        print(f"Product location: {result[0][5]}")  # skipping stock
                        print(f"Product supplier: {result[0][6]}")
                        print(f"Product status: {status_display}")
                        print("")
                        print("Barcode:")
                        generate_barcode_to_terminal(result[0][3])  # Assuming barcode is at index 3
                    else:
                        print("Product details are incomplete.")
                else:
                    print("Product not found.")
                    time.sleep(0.5)
                    viewProductDetails()
            
            else:
                cursor.execute("SELECT * FROM products WHERE product_code=?", (VPD_code.upper(),))
                result = cursor.fetchall()

                if result:
                    if len(result[0]) > 7:  # Ensure there are enough columns in the result
                        status = result[0][7]  # Get status from the first product
                        if status.lower() == "active":
                            status_display = bcolors.OKGREEN + "██ ACTIVE" + bcolors.ENDC
                        elif status.lower() == "inactive":
                            status_display = bcolors.FAIL + "██ INACTIVE" + bcolors.ENDC
                        else:
                            status_display = status

                        # Accessing product details safely
                        print("")
                        print(f"Product name: {result[0][1]}")
                        print(f"Product code: {result[0][2]}")
                        print(f"Product EAN: {result[0][3]}")
                        print(f"Product location: {result[0][5]}")  # skipping stock
                        print(f"Product supplier: {result[0][6]}")
                        print(f"Product status: {status_display}")
                        print("")
                    else:
                        print("Product details are incomplete.")
                else:
                    print("Product not found.")
                    time.sleep(0.5)
                    viewProductDetails()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(0.5)
            viewProductDetails()

def removeProduct():
    console_clear()
    print("Remove product:")
    print("")
    rp_pcode = input("Enter the product code or EAN of the product you want to delete (or press Enter to cancel): ")

    if rp_pcode == "":
        menu()

    #wipe db function:
    elif rp_pcode.lower() == "drop table":
        the_choice = input("Are you sure? This action can NOT be undone! (Y/N) ")
        if the_choice.lower() == "y":
            print("")
            the_second_choice = input("This will quite literally remove everything. are you SURE you want to do this? (Y/N) ")
            if the_second_choice.lower() == "y":
                print("")
                the_last_choice = input("To confirm, please write 'I am fully aware this will delete the database' ")
                if the_last_choice.lower() == "i am fully aware this will delete the database":
                    cursor.execute("DROP TABLE products")
                    conn.commit()
                    for i in range(5):
                        console_clear()
                        print("Table dropped. This action requires a full restart of Stockfox. Please relaunch the program.")
                        print("")
                        print(f"Closing Stockfox in {5-i} seconds...")
                        time.sleep(1)
                    exit()

                else:
                    removeProduct()
            else:
                removeProduct()
        else:
            removeProduct()

    try:
        if rp_pcode == "":
            menu()

        elif rp_pcode.isdigit():
            cursor.execute("SELECT product_name FROM products WHERE ean=?", (rp_pcode,))
            result = cursor.fetchone()
            
            if result:
                confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
                if confirmation_delete.lower() == "y":
                    cursor.execute("DELETE FROM products WHERE ean=?", (rp_pcode,))
                    print("Product deleted")
                    conn.commit()  # Commit after delete
            else:
                print("Product not found.")
                time.sleep(0.5)
                removeProduct()
        
        else:
            cursor.execute("SELECT product_name FROM products WHERE product_code=?", (rp_pcode.upper(),))
            result = cursor.fetchone()

            if result:
                confirmation_delete = input(f"Are you sure you want to delete {result[0]}? (Y/N): ")
                if confirmation_delete.lower() == "y":
                    cursor.execute("DELETE FROM products WHERE product_code=?", (rp_pcode.upper(),))
                    print(f"{result[0]} was deleted")
                    conn.commit()  # Commit after delete
                    time.sleep(0.5)
                    menu()
                else:
                    removeProduct()
            else:
                print("Product not found.")
                time.sleep(0.5)
                removeProduct()
        
    except Exception as e:
        print(f"An error occurred: {e}")



def settings():
    console_clear()
    print("---------- StockFox ----------")
    print("2024 © Lien Vending Solutions")
    print("Version Beta 1.0")
    print("Made in Norway ♥")
    print("")
    print("Support: stockfox@lienvending.solutions")
    print("")
    pressAnyKeyForMenu()

menu()