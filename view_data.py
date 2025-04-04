import sqlite3
from tabulate import tabulate

def view_database():
    # Connect to the database
    conn = sqlite3.connect('cloth_shop.db')
    cursor = conn.cursor()
    
    print("\n=== CUSTOMERS ===")
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    if customers:
        print(tabulate(customers, headers=['ID', 'Name', 'Phone', 'Total Bill', 'Date'], tablefmt='grid'))
    else:
        print("No customers found")
    
    print("\n=== BILLS ===")
    cursor.execute("SELECT * FROM bills")
    bills = cursor.fetchall()
    if bills:
        print(tabulate(bills, headers=['Bill ID', 'Customer Name', 'Phone', 'Date', 'Amount', 'Payment Method'], tablefmt='grid'))
    else:
        print("No bills found")
    
    print("\n=== BILL ITEMS ===")
    cursor.execute("""
        SELECT bi.*, p.name as product_name 
        FROM bill_items bi 
        JOIN products p ON bi.product_id = p.product_id
    """)
    bill_items = cursor.fetchall()
    if bill_items:
        print(tabulate(bill_items, headers=['Item ID', 'Bill ID', 'Product ID', 'Quantity', 'Price', 'Product Name'], tablefmt='grid'))
    else:
        print("No bill items found")
    
    print("\n=== PRODUCTS ===")
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    if products:
        print(tabulate(products, headers=['ID', 'Name', 'Category', 'Price', 'Stock', 'Description'], tablefmt='grid'))
    else:
        print("No products found")
    
    conn.close()

if __name__ == "__main__":
    try:
        view_database()
    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
    except Exception as e:
        print(f"An error occurred: {e}") 