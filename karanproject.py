import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import sqlite3
from datetime import datetime
import os

class ClothShopBillingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("FashionFabric Billing System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f8ff")
        
        # Create database and tables if they don't exist
        self.create_database()
        
        # Load images (placeholder paths - replace with your actual image paths)
        self.logo_img = PhotoImage(file="logo.png").subsample(2, 2) if os.path.exists("logo.png") else None
        self.tshirt_img = PhotoImage(file="tshirt.png").subsample(4, 4) if os.path.exists("tshirt.png") else None
        self.pants_img = PhotoImage(file="pants.png").subsample(4, 4) if os.path.exists("pants.png") else None
        self.dress_img = PhotoImage(file="dress.png").subsample(4, 4) if os.path.exists("dress.png") else None
        
        # Create UI elements
        self.create_header()
        self.create_product_section()
        self.create_bill_section()
        self.create_customer_section()
        self.create_buttons()
        
        # Initialize variables
        self.total_items = 0
        self.total_amount = 0.0
        self.current_bill_items = []
    
    def create_database(self):
        """Create database and tables if they don't exist"""
        self.conn = sqlite3.connect('cloth_shop.db')
        self.cursor = self.conn.cursor()
        
        # Create products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                description TEXT
            )
        ''')
        
        # Create customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                total_bill REAL DEFAULT 0.0,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create bills table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                customer_phone TEXT,
                bill_date TEXT,
                total_amount REAL,
                payment_method TEXT
            )
        ''')
        
        # Create bill_items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bill_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price REAL,
                FOREIGN KEY(bill_id) REFERENCES bills(bill_id),
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            )
        ''')
        
        # Insert some sample products if table is empty
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            sample_products = [
                ("Cotton T-Shirt", "T-Shirt", 149.99, 50, "100% Cotton, Regular Fit"),
                ("Denim Jeans", "Pants", 290.99, 30, "Slim Fit, Stretch Denim"),
                ("Summer Dress", "Dress", 249.99, 25, "Floral Print, Lightweight"),
                ("Formal Shirt", "Shirt", 199.99, 40, "Office Wear, Iron-Free"),
                ("Sports Shorts", "Shorts", 140.99, 35, "Quick Dry, Elastic Waist")
            ]
            self.cursor.executemany(
                "INSERT INTO products (name, category, price, stock, description) VALUES (?, ?, ?, ?, ?)",
                sample_products
            )
            self.conn.commit()
        
        self.conn.commit()
    
    def save_customer(self, name, phone, total_bill):
        """Save customer information to the database"""
        try:
            self.cursor.execute('''
                INSERT INTO customers (name, phone, total_bill)
                VALUES (?, ?, ?)
            ''', (name, phone, total_bill))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to save customer: {str(e)}")
            return False
    
    def get_customer_by_phone(self, phone):
        """Retrieve customer information by phone number"""
        try:
            self.cursor.execute('''
                SELECT * FROM customers WHERE phone = ?
            ''', (phone,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to retrieve customer: {str(e)}")
            return None
    
    def update_customer_bill(self, phone, total_bill):
        """Update customer's total bill"""
        try:
            self.cursor.execute('''
                UPDATE customers 
                SET total_bill = total_bill + ?
                WHERE phone = ?
            ''', (total_bill, phone))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to update customer bill: {str(e)}")
            return False
    
    def create_header(self):
        """Create the header section with logo and title"""
        header_frame = tk.Frame(self.root, bg="#4682b4", height=100)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        if self.logo_img:
            logo_label = tk.Label(header_frame, image=self.logo_img, bg="#4682b4")
            logo_label.pack(side=tk.LEFT, padx=20)
        
        title_label = tk.Label(
            header_frame, 
            text="FashionFabric Billing System", 
            font=("Arial", 24, "bold"), 
            fg="white", 
            bg="#4682b4"
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        date_label = tk.Label(
            header_frame, 
            text=datetime.now().strftime("%d/%m/%Y %H:%M"), 
            font=("Arial", 12), 
            fg="white", 
            bg="#4682b4"
        )
        date_label.pack(side=tk.RIGHT, padx=20)
    
    def create_product_section(self):
        """Create the product selection section"""
        product_frame = tk.LabelFrame(
            self.root, 
            text="Products", 
            font=("Arial", 12, "bold"), 
            bg="#f0f8ff", 
            padx=10, 
            pady=10
        )
        product_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        # Product categories with images
        categories_frame = tk.Frame(product_frame, bg="#f0f8ff")
        categories_frame.pack(fill=tk.X, pady=5)
        
        category_buttons = [
            ("T-Shirts", self.tshirt_img, "T-Shirt"),
            ("Pants", self.pants_img, "Pants"),
            ("Dresses", self.dress_img, "Dress"),
            ("All Products", None, "")
        ]
        
        for text, img, category in category_buttons:
            btn = ttk.Button(
                categories_frame,
                text=text,
                image=img,
                compound=tk.TOP if img else tk.LEFT,
                command=lambda c=category: self.filter_products(c)
            )
            btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        # Product search
        search_frame = tk.Frame(product_frame, bg="#f0f8ff")
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search:", bg="#f0f8ff").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            search_frame, 
            text="Search", 
            command=self.search_products
        ).pack(side=tk.LEFT, padx=5)
        
        # Product treeview
        self.product_tree = ttk.Treeview(
            product_frame,
            columns=("id", "name", "category", "price", "stock"),
            show="headings",
            height=8
        )
        
        self.product_tree.heading("id", text="ID")
        self.product_tree.heading("name", text="Product Name")
        self.product_tree.heading("category", text="Category")
        self.product_tree.heading("price", text="Price ($)")
        self.product_tree.heading("stock", text="Stock")
        
        self.product_tree.column("id", width=50, anchor=tk.CENTER)
        self.product_tree.column("name", width=200)
        self.product_tree.column("category", width=100)
        self.product_tree.column("price", width=80, anchor=tk.CENTER)
        self.product_tree.column("stock", width=60, anchor=tk.CENTER)
        
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.product_tree, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate products
        self.filter_products("")
        
        # Bind double click to add product to bill
        self.product_tree.bind("<Double-1>", self.add_to_bill)
    
    def create_bill_section(self):
        """Create the bill section"""
        bill_frame = tk.LabelFrame(
            self.root, 
            text="Current Bill", 
            font=("Arial", 12, "bold"), 
            bg="#f0f8ff", 
            padx=10, 
            pady=10
        )
        bill_frame.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        
        # Bill treeview
        self.bill_tree = ttk.Treeview(
            bill_frame,
            columns=("id", "name", "price", "quantity", "total"),
            show="headings",
            height=5
        )
        
        self.bill_tree.heading("id", text="ID")
        self.bill_tree.heading("name", text="Product Name")
        self.bill_tree.heading("price", text="Price ($)")
        self.bill_tree.heading("quantity", text="Qty")
        self.bill_tree.heading("total", text="Total ($)")
        
        self.bill_tree.column("id", width=50, anchor=tk.CENTER)
        self.bill_tree.column("name", width=200)
        self.bill_tree.column("price", width=80, anchor=tk.CENTER)
        self.bill_tree.column("quantity", width=60, anchor=tk.CENTER)
        self.bill_tree.column("total", width=80, anchor=tk.CENTER)
        
        self.bill_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bill summary
        summary_frame = tk.Frame(bill_frame, bg="#f0f8ff")
        summary_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            summary_frame, 
            text="Total Items:", 
            font=("Arial", 10, "bold"), 
            bg="#f0f8ff"
        ).pack(side=tk.LEFT, padx=5)
        
        self.total_items_label = tk.Label(
            summary_frame, 
            text="0", 
            font=("Arial", 10), 
            bg="#f0f8ff"
        )
        self.total_items_label.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            summary_frame, 
            text="Total Amount:", 
            font=("Arial", 10, "bold"), 
            bg="#f0f8ff"
        ).pack(side=tk.LEFT, padx=(20, 5))
        
        self.total_amount_label = tk.Label(
            summary_frame, 
            text="$0.00", 
            font=("Arial", 10), 
            bg="#f0f8ff"
        )
        self.total_amount_label.pack(side=tk.LEFT, padx=5)
    
    def create_customer_section(self):
        """Create customer details section"""
        customer_frame = tk.Frame(self.root, bg="#f0f8ff")
        customer_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            customer_frame, 
            text="Customer Name:", 
            bg="#f0f8ff"
        ).grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        
        self.customer_name = ttk.Entry(customer_frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(
            customer_frame, 
            text="Phone:", 
            bg="#f0f8ff"
        ).grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        
        self.customer_phone = ttk.Entry(customer_frame, width=20)
        self.customer_phone.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(
            customer_frame, 
            text="Payment Method:", 
            bg="#f0f8ff"
        ).grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
        
        self.payment_method = ttk.Combobox(
            customer_frame, 
            values=["Cash", "Credit Card", "Debit Card", "Mobile Payment"], 
            width=15
        )
        self.payment_method.grid(row=0, column=5, padx=5, pady=5)
        self.payment_method.current(0)
    
    def create_buttons(self):
        """Create action buttons"""
        button_frame = tk.Frame(self.root, bg="#f0f8ff")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Add to Bill", 
            command=self.add_to_bill
        ).pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        ttk.Button(
            button_frame, 
            text="Remove Item", 
            command=self.remove_from_bill
        ).pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        ttk.Button(
            button_frame, 
            text="Clear Bill", 
            command=self.clear_bill
        ).pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        ttk.Button(
            button_frame, 
            text="Generate Bill", 
            command=self.generate_bill,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=5)
        
        # Configure accent button style
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="white", background="#4CAF50", font=("Arial", 10, "bold"))
    
    def filter_products(self, category):
        """Filter products by category"""
        if category:
            self.cursor.execute(
                "SELECT product_id, name, category, price, stock FROM products WHERE category=?",
                (category,)
            )
        else:
            self.cursor.execute("SELECT product_id, name, category, price, stock FROM products")
        
        products = self.cursor.fetchall()
        self.update_product_tree(products)
    
    def search_products(self):
        """Search products by name"""
        search_term = self.search_entry.get()
        self.cursor.execute(
            "SELECT product_id, name, category, price, stock FROM products WHERE name LIKE ?",
            (f"%{search_term}%",)
        )
        products = self.cursor.fetchall()
        self.update_product_tree(products)
    
    def update_product_tree(self, products):
        """Update the product treeview with given products"""
        self.product_tree.delete(*self.product_tree.get_children())
        for product in products:
            self.product_tree.insert("", tk.END, values=product)
    
    def add_to_bill(self, event=None):
        """Add selected product to the bill"""
        selected_item = self.product_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a product to add to bill")
            return
        
        product_data = self.product_tree.item(selected_item, "values")
        product_id, name, category, price, stock = product_data
        
        # Check if product already in bill
        for item in self.current_bill_items:
            if item["product_id"] == product_id:
                # Ask for quantity to add
                quantity = self.ask_quantity(name, current_qty=item["quantity"])
                if quantity is None:
                    return
                
                # Update existing item
                item["quantity"] += quantity
                item["total"] = float(price) * item["quantity"]
                
                # Update treeview
                for child in self.bill_tree.get_children():
                    if self.bill_tree.item(child, "values")[0] == product_id:
                        self.bill_tree.item(
                            child, 
                            values=(
                                product_id, 
                                name, 
                                price, 
                                item["quantity"], 
                                f"{item['total']:.2f}"
                            )
                        )
                        break
                
                self.update_totals()
                return
        
        # If product not already in bill
        quantity = self.ask_quantity(name)
        if quantity is None:
            return
        
        # Add new item to bill
        total_price = float(price) * quantity
        self.current_bill_items.append({
            "product_id": product_id,
            "name": name,
            "price": float(price),
            "quantity": quantity,
            "total": total_price
        })
        
        # Add to treeview
        self.bill_tree.insert(
            "", 
            tk.END, 
            values=(
                product_id, 
                name, 
                price, 
                quantity, 
                f"{total_price:.2f}"
            )
        )
        
        self.update_totals()
    
    def ask_quantity(self, product_name, current_qty=0):
        """Show dialog to ask for quantity"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Enter Quantity")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        
        tk.Label(
            dialog, 
            text=f"Enter quantity for {product_name}:",
            font=("Arial", 10)
        ).pack(pady=10)
        
        quantity_var = tk.StringVar(value=str(current_qty + 1) if current_qty else "1")
        quantity_entry = ttk.Entry(
            dialog, 
            textvariable=quantity_var, 
            font=("Arial", 12), 
            width=10,
            justify=tk.CENTER
        )
        quantity_entry.pack(pady=10)
        quantity_entry.select_range(0, tk.END)
        quantity_entry.focus()
        
        def on_ok():
            try:
                qty = int(quantity_var.get())
                if qty <= 0:
                    raise ValueError
                dialog.quantity = qty
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive number")
        
        def on_cancel():
            dialog.quantity = None
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame, 
            text="OK", 
            command=on_ok
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=on_cancel
        ).pack(side=tk.LEFT, padx=10)
        
        dialog.wait_window()
        return getattr(dialog, "quantity", None)
    
    def remove_from_bill(self):
        """Remove selected item from bill"""
        selected_item = self.bill_tree.focus()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        product_id = self.bill_tree.item(selected_item, "values")[0]
        
        # Remove from current items list
        self.current_bill_items = [
            item for item in self.current_bill_items 
            if str(item["product_id"]) != product_id
        ]
        
        # Remove from treeview
        self.bill_tree.delete(selected_item)
        
        self.update_totals()
    
    def clear_bill(self):
        """Clear the current bill"""
        if not self.current_bill_items:
            return
            
        if messagebox.askyesno(
            "Confirm", 
            "Are you sure you want to clear the current bill?"
        ):
            self.current_bill_items = []
            self.bill_tree.delete(*self.bill_tree.get_children())
            self.update_totals()
    
    def update_totals(self):
        """Update the total items and amount labels"""
        self.total_items = sum(item["quantity"] for item in self.current_bill_items)
        self.total_amount = sum(item["total"] for item in self.current_bill_items)
        
        self.total_items_label.config(text=str(self.total_items))
        self.total_amount_label.config(text=f"${self.total_amount:.2f}")
    
    def generate_bill(self):
        """Generate and save the bill to database"""
        if not self.current_bill_items:
            messagebox.showwarning("Warning", "No items in the bill to generate")
            return
            
        customer_name = self.customer_name.get().strip()
        customer_phone = self.customer_phone.get().strip()
        payment_method = self.payment_method.get()
        
        if not customer_name:
            messagebox.showwarning("Warning", "Please enter customer name")
            return
        
        try:
            # Save bill to database
            bill_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO bills (customer_name, customer_phone, bill_date, total_amount, payment_method) VALUES (?, ?, ?, ?, ?)",
                (customer_name, customer_phone, bill_date, self.total_amount, payment_method)
            )
            bill_id = self.cursor.lastrowid
            
            # Save bill items
            for item in self.current_bill_items:
                self.cursor.execute(
                    "INSERT INTO bill_items (bill_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                    (bill_id, item["product_id"], item["quantity"], item["price"])
                )
                
                # Update product stock
                self.cursor.execute(
                    "UPDATE products SET stock = stock - ? WHERE product_id = ?",
                    (item["quantity"], item["product_id"])
                )
            
            self.conn.commit()
            
            # Show success message
            messagebox.showinfo(
                "Success", 
                f"Bill generated successfully!\n\n"
                f"Bill ID: {bill_id}\n"
                f"Customer: {customer_name}\n"
                f"Total Amount: ${self.total_amount:.2f}"
            )
            
            # Clear current bill
            self.clear_bill()
            self.customer_name.delete(0, tk.END)
            self.customer_phone.delete(0, tk.END)
            self.payment_method.current(0)
            
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to generate bill: {str(e)}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = ClothShopBillingSystem(root)
    
    # Configure ttk style for modern look
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#f0f8ff")
    style.configure("TLabel", background="#f0f8ff")
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
    
    root.mainloop()