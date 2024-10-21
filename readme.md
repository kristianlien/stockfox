```
    _____ _             _    ______        
   / ____| |           | |  |  ____|       
  | (___ | |_ ___   ___| | _| |__ _____  __
   \___ \| __/ _ \ / __| |/ /  __/ _ \ \/ /
   ____) | || (_) | (__|   <| | | (_) >  < 
  |_____/ \__\___/ \___|_|\_\_|  \___/_/\_\
```
Stockfox is a logistics management software designed to be light, minimal and user friendly. It uses both SKU (called "Product codes" in the software) and barcodes (called "EAN" in the software). It works with most consumer grade barcode scanners, and is designed to run optimally even on very weak systems. It has no GUI, instead utilizing a command-line interface for interacting with the system. The "Units" in the system can either be storage units or consumer units, but not both. It's reccomended to use StockFox with consumer units.

### Minimal System Requirements:
- 1 GHz single-core processor
- 2 GB RAM
- 100mb Disk Space (10 GB is needed to install Python)
- Python 3

## Installation

Unpack the ZIP file into the folder you where you want to install StockFox. Then run the .py file or the .bat file, depending on your version of Python. (These essentially do the same thing, but if there are some permission issues, the .py file might not work.)

## Instructions
When you launch StockFox for the very first time, it will automatically generate a database. This file is **current_inventory.db** and contains all the data used by StockFox. This is database has 9 rows.
These rows are:
```
product_name, product_code, ean, current_stock, location, supplier, status, unit_price, sale_price
```

## Functions:
1. View current stock
Displays all products, stock quantities, locations and product status for each product.
2. Generate picklist
Generates a picklist 
3. Update individual product stock
4. Update/add inventory from new shipment
5. Insert new product into system
6: Edit products
7: View product details
8: Remove product from system
9: Settings/information

### Adding a product
To add a product, first press 5 on the main menu.
Then, type the product name, product code (A-Z, must be unique), and scan the barcode. Most consumer grade barcode scanners will input the number as a keyboard input, and then press enter automatically. This is most practical when using StockFox.

Then input the unit quantity, and set product status. Then you can set the location. Afterwards, input the stock price from supplier, and sale price. 

(It's reccomended to input both units either before or after VAT, to ensure price calculations are accurate.)

Afterwards, set the product status. Usually this is set to either A (which stands for Active) or I (which stands for Inactive). You can also set a custom product status (ie. "Sold out from supplier", "Waiting for refill")

To exit, type "exit" into any of the fields.

### Editing a product
To edit a product, press 6 on the main menu, then enter the product code for the product you want to edit.
Then, enter the number corresponding to the line you want to edit.
Afterwards, type the new entry for the line, and it will save automatically.

To exit, press enter before writing in a product code. If you want to exit after entering a product code, type "0".

### Deleting a product
To delete a product, press 8 from the menu, and type in the product code. Confirm with "Y" if the product thats selected is correct.

### Update product stock
Here, you can choose to either change quantity, or add quantity.

To change quantity, choose 3 from the menu. Then type in the product code, and how many are in stock. This will change the "current_stock" entry to the number specified.

To add quantity, choose 4 from the menu. Type in the product code, then type in how many that you want to *add* to the inventory. This is added to the current quantity, instead of replacing the original value.

### View product stock
Press 1 from the menu, and the system will display all products, stock quantities, locations and product status for each product.

### Generate picklist
Press 2 from the menu, and type in the product code you want to add to the current picklist.
It will then display the current quantity in storage. This can not be exceeded in the picklist.
Type in the quantity for the selected product, then press enter. Repeat the process until you have all the products you want. Then, press enter without typing in a product code. This will generate the picklist.

The picklist thats generated will have a default header. To change this, go to line 315 in prototype.py and change this entry:
```HTML
<img src="https://files.catbox.moe/x46dlm.png" alt="Company Logo" style="width:1250;"> 
```
(Replace the catbox.moe file to the image link you want)

### View product details
Press 7 from the menu, then either enter the product code or scan a barcode. The system will then output all information about the product except for quantity. Quantity is read from the "View stock" function.
To change anything, use the "edit product" function.


### Advanced features
1. Go to the "edit product" function, and type in SQL. From here, you can input custom SQL commands to do whatever you want. Type "exit" to go back to the menu
2. Go to the "delete product" function, and write in "Drop Table". This will delete the entire database.
3. Go to the "edit product" function and enter "ADD EAN". You can from there rapidly add barcodes to products.
4. Go to the "edit product" function and write "EXPORT". This will export the entire DB into a csv file in the StockFox folder.

## Technical specifications
StockFox utilizes a SQLite3 database with 10 rows.

Sample Schema:
```sql
CREATE TABLE IF NOT EXISTS products (
    product_name TEXT,
    product_code TEXT UNIQUE,
    ean TEXT UNIQUE,
    stock INTEGER,
    location TEXT,
    supplier TEXT,
    status TEXT,
    unit_price REAL,
    sale_price REAL
);
```
To make any big or advanced changes, you can input custom SQL by typing "SQL" into the "edit product" function.

## Exception Handling:
Each function includes robust exception handling to catch potential errors during database operations. For example, if a product is not found, or if an invalid SQL command is entered, the system gracefully informs the user and returns to the main menu.

Sample Exception Handling:

```python
except Exception as e:
    print(f"An error occurred: {e}")
    time.sleep(0.5)
```
## Security Considerations:
The system includes a few important security measures:

### SQL Command Warning: 
In the editProduct() function, custom SQL commands are allowed but only with warnings to avoid dangerous commands (e.g., DROP).
Unique Constraints: The database schema enforces unique constraints on product_code and ean to prevent duplicate entries.