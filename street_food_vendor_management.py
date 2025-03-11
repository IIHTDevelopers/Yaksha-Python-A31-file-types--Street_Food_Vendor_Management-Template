"""
Street Food Vendor Management System

This module implements a system for street food vendors to track inventory,
sales, customer feedback, and daily operations using various file operations.
"""

import os
import csv
import datetime


def read_inventory(file_path):
    """
    Read inventory data from a text file.
    
    Args:
        file_path: Path to the inventory file
        
    Returns:
        Dictionary mapping item names to their quantities and prices
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Inventory file not found: {file_path}")
    
    inventory = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split(',')
                    if len(parts) != 3:
                        raise ValueError(f"Invalid line format: {line}")
                    
                    item_name, quantity, price = parts
                    inventory[item_name] = {
                        'quantity': int(quantity),
                        'price': float(price)
                    }
        return inventory
    except ValueError as e:
        raise ValueError(f"Error parsing inventory data: {e}")


def update_inventory(file_path, item_name, quantity, price):
    """
    Update or add an item to the inventory file.
    
    Args:
        file_path: Path to the inventory file
        item_name: Name of the food item
        quantity: Quantity available
        price: Price per unit
        
    Raises:
        ValueError: If any required fields are invalid
    """
    if not item_name:
        raise ValueError("Item name cannot be empty")
    
    try:
        quantity = int(quantity)
        price = float(price)
    except ValueError:
        raise ValueError("Quantity must be an integer and price must be a number")

    # Read existing inventory
    inventory = {}
    if os.path.exists(file_path):
        inventory = read_inventory(file_path)
    
    # Update inventory
    inventory[item_name] = {'quantity': quantity, 'price': price}
    
    # Write updated inventory back to file
    with open(file_path, 'w') as file:
        file.write("# Inventory - format: item_name,quantity,price\n")
        for item, details in inventory.items():
            file.write(f"{item},{details['quantity']},{details['price']}\n")


def log_sale(file_path, item_name, quantity, total_price):
    """
    Log a sale to the sales log file (append mode).
    
    Args:
        file_path: Path to the sales log file
        item_name: Name of the item sold
        quantity: Quantity sold
        total_price: Total price of the sale
        
    Raises:
        ValueError: If any required fields are invalid
    """
    if not item_name or quantity <= 0 or total_price <= 0:
        raise ValueError("Invalid sale data")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(file_path)
    
    try:
        with open(file_path, 'a') as file:
            if not file_exists:
                file.write("timestamp,item_name,quantity,total_price\n")
            file.write(f"{timestamp},{item_name},{quantity},{total_price}\n")
    except IOError as e:
        raise IOError(f"Error writing to sales log: {e}")


def save_customer_feedback(file_path, customer_name, rating, comments):
    """
    Save customer feedback to a text file.
    
    Args:
        file_path: Path to the feedback file
        customer_name: Name of the customer
        rating: Rating (1-5)
        comments: Customer comments
        
    Raises:
        ValueError: If rating is not between 1 and 5
    """
    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
    except ValueError:
        raise ValueError("Rating must be an integer between 1 and 5")
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(file_path, 'a') as file:
            file.write(f"===== FEEDBACK: {timestamp} =====\n")
            file.write(f"Customer: {customer_name}\n")
            file.write(f"Rating: {rating}/5\n")
            file.write(f"Comments: {comments}\n\n")
    except IOError as e:
        raise IOError(f"Error saving feedback: {e}")


def read_sales_report(file_path):
    """
    Read sales data from a CSV file and generate a summary.
    
    Args:
        file_path: Path to the sales CSV file
        
    Returns:
        Dictionary with sales summary (total revenue, items sold, etc.)
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Sales file not found: {file_path}")
    
    try:
        total_revenue = 0
        item_counts = {}
        
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item_name = row['item_name']
                quantity = int(row['quantity'])
                total_price = float(row['total_price'])
                
                total_revenue += total_price
                
                if item_name in item_counts:
                    item_counts[item_name] += quantity
                else:
                    item_counts[item_name] = quantity
        
        # Find best-selling item
        best_seller = max(item_counts.items(), key=lambda x: x[1]) if item_counts else None
        
        return {
            'total_revenue': total_revenue,
            'items_sold': sum(item_counts.values()),
            'unique_items': len(item_counts),
            'best_seller': best_seller,
            'item_breakdown': item_counts
        }
    except (csv.Error, ValueError) as e:
        raise ValueError(f"Error processing sales data: {e}")


def generate_daily_report(inventory_file, sales_file, report_file, date):
    """
    Generate a daily report with inventory and sales information.
    
    Args:
        inventory_file: Path to the inventory file
        sales_file: Path to the sales file
        report_file: Path where the report will be saved
        date: Date for the report (YYYY-MM-DD format)
        
    Raises:
        FileNotFoundError: If required files don't exist
    """
    try:
        # Load inventory and sales data
        inventory = read_inventory(inventory_file)
        
        # Filter sales for the specified date
        daily_sales = []
        
        with open(sales_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['timestamp'].startswith(date):
                    daily_sales.append(row)
        
        # Calculate daily totals
        total_revenue = sum(float(sale['total_price']) for sale in daily_sales)
        
        # Generate the report
        with open(report_file, 'w') as file:
            file.write(f"DAILY SALES REPORT - {date}\n")
            file.write("=" * 50 + "\n\n")
            
            file.write("SALES SUMMARY\n")
            file.write(f"Total Revenue: ${total_revenue:.2f}\n")
            file.write(f"Number of Sales: {len(daily_sales)}\n\n")
            
            file.write("INVENTORY STATUS\n")
            for item, details in inventory.items():
                file.write(f"{item}: {details['quantity']} units at ${details['price']:.2f} each\n")
            
            file.write("\nDETAILED SALES\n")
            for sale in daily_sales:
                file.write(f"{sale['timestamp']} - {sale['item_name']} x{sale['quantity']} - ${float(sale['total_price']):.2f}\n")
    
    except (FileNotFoundError, IOError) as e:
        raise Exception(f"Error generating report: {e}")


def search_feedback(file_path, search_term):
    """
    Search customer feedback for a specific term.
    
    Args:
        file_path: Path to the feedback file
        search_term: Term to search for
        
    Returns:
        List of feedback entries containing the search term
        
    Raises:
        FileNotFoundError: If the file does not exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Feedback file not found: {file_path}")
    
    results = []
    current_feedback = {}
    
    try:
        with open(file_path, 'r') as file:
            collecting = False
            
            for line in file:
                line = line.strip()
                
                if line.startswith("===== FEEDBACK:"):
                    # Start of a new feedback entry
                    if collecting and search_term.lower() in ' '.join(current_feedback.values()).lower():
                        results.append(current_feedback.copy())
                    
                    current_feedback = {}
                    collecting = True
                    current_feedback["timestamp"] = line.split("FEEDBACK: ")[1].strip("=").strip()
                elif collecting and line.startswith("Customer:"):
                    current_feedback["customer"] = line.split("Customer: ")[1]
                elif collecting and line.startswith("Rating:"):
                    current_feedback["rating"] = line.split("Rating: ")[1]
                elif collecting and line.startswith("Comments:"):
                    current_feedback["comments"] = line.split("Comments: ")[1]
                elif line == "" and collecting:
                    # End of the current feedback
                    if search_term.lower() in ' '.join(current_feedback.values()).lower():
                        results.append(current_feedback.copy())
                    collecting = False
        
        # Check the last feedback entry if we're still collecting
        if collecting and search_term.lower() in ' '.join(current_feedback.values()).lower():
            results.append(current_feedback.copy())
            
        return results
    except IOError as e:
        raise IOError(f"Error reading feedback file: {e}")


def backup_data_files(source_dir, backup_dir):
    """
    Create backups of all data files in the source directory.
    
    Args:
        source_dir: Directory containing the data files
        backup_dir: Directory where backups will be stored
        
    Returns:
        Number of files backed up
        
    Raises:
        IOError: If directories don't exist or backup fails
    """
    if not os.path.exists(source_dir):
        raise IOError(f"Source directory not found: {source_dir}")
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_count = 0
    
    try:
        for filename in os.listdir(source_dir):
            if filename.endswith(('.txt', '.csv')):
                source_path = os.path.join(source_dir, filename)
                backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
                backup_path = os.path.join(backup_dir, backup_name)
                
                with open(source_path, 'r') as source, open(backup_path, 'w') as backup:
                    backup.write(source.read())
                
                backup_count += 1
        
        return backup_count
    except IOError as e:
        raise IOError(f"Backup operation failed: {e}")


def main():
    """
    Main function demonstrating the use of all file handling operations.
    """
    # Define file paths
    data_dir = "vendor_data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    inventory_file = os.path.join(data_dir, "inventory.txt")
    sales_file = os.path.join(data_dir, "sales.csv")
    feedback_file = os.path.join(data_dir, "feedback.txt")
    report_file = os.path.join(data_dir, "daily_report.txt")
    backup_dir = os.path.join(data_dir, "backups")
    
    while True:
        print("\n===== STREET FOOD VENDOR MANAGEMENT SYSTEM =====")
        print("1. View Inventory")
        print("2. Update Inventory Item")
        print("3. Record Sale")
        print("4. Submit Customer Feedback")
        print("5. Generate Sales Report")
        print("6. Generate Daily Report")
        print("7. Search Feedback")
        print("8. Backup Data Files")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ")
        
        try:
            if choice == '1':
                # View inventory
                inventory = read_inventory(inventory_file)
                print("\nCurrent Inventory:")
                for item, details in inventory.items():
                    print(f"{item}: {details['quantity']} units at ${details['price']:.2f} each")
            
            elif choice == '2':
                # Update inventory
                item_name = input("Enter item name: ")
                quantity = input("Enter quantity: ")
                price = input("Enter price: ")
                update_inventory(inventory_file, item_name, quantity, price)
                print(f"Inventory updated for {item_name}")
            
            elif choice == '3':
                # Record sale
                item_name = input("Enter item name: ")
                quantity = int(input("Enter quantity sold: "))
                
                # Check inventory
                inventory = read_inventory(inventory_file)
                if item_name not in inventory:
                    print(f"Error: {item_name} not found in inventory")
                    continue
                
                if inventory[item_name]['quantity'] < quantity:
                    print(f"Error: Not enough {item_name} in inventory")
                    continue
                
                price = inventory[item_name]['price']
                total_price = price * quantity
                
                # Record the sale
                log_sale(sales_file, item_name, quantity, total_price)
                
                # Update inventory
                new_quantity = inventory[item_name]['quantity'] - quantity
                update_inventory(inventory_file, item_name, new_quantity, price)
                
                print(f"Sale recorded: {quantity} {item_name} for ${total_price:.2f}")
            
            elif choice == '4':
                # Submit feedback
                customer_name = input("Enter customer name: ")
                rating = input("Enter rating (1-5): ")
                comments = input("Enter comments: ")
                save_customer_feedback(feedback_file, customer_name, rating, comments)
                print("Feedback saved successfully")
            
            elif choice == '5':
                # Generate sales report
                if os.path.exists(sales_file):
                    report = read_sales_report(sales_file)
                    print("\nSales Report:")
                    print(f"Total Revenue: ${report['total_revenue']:.2f}")
                    print(f"Items Sold: {report['items_sold']}")
                    print(f"Unique Items: {report['unique_items']}")
                    
                    if report['best_seller']:
                        print(f"Best Seller: {report['best_seller'][0]} ({report['best_seller'][1]} units)")
                    
                    print("\nItem Breakdown:")
                    for item, count in report['item_breakdown'].items():
                        print(f"{item}: {count} units")
                else:
                    print("No sales data available")
            
            elif choice == '6':
                # Generate daily report
                date = input("Enter date (YYYY-MM-DD): ")
                generate_daily_report(inventory_file, sales_file, report_file, date)
                print(f"Daily report generated as {report_file}")
            
            elif choice == '7':
                # Search feedback
                search_term = input("Enter search term: ")
                results = search_feedback(feedback_file, search_term)
                
                print(f"\nFound {len(results)} feedback entries containing '{search_term}':")
                for i, feedback in enumerate(results, 1):
                    print(f"\n{i}. Date: {feedback['timestamp']}")
                    print(f"   Customer: {feedback['customer']}")
                    print(f"   Rating: {feedback['rating']}")
                    print(f"   Comments: {feedback['comments']}")
            
            elif choice == '8':
                # Backup data files
                count = backup_data_files(data_dir, backup_dir)
                print(f"{count} files backed up to {backup_dir}")
            
            elif choice == '9':
                # Exit
                print("Thank you for using the Street Food Vendor Management System")
                break
            
            else:
                print("Invalid choice. Please enter a number between 1 and 9.")
        
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()