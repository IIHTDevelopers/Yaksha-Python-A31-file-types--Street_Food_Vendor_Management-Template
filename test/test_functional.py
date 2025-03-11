import os
import tempfile
import pytest
from test.TestUtils import TestUtils
from street_food_vendor_management import read_inventory, update_inventory, log_sale, save_customer_feedback, read_sales_report, generate_daily_report, backup_data_files, search_feedback


def test_inventory_operations():
    """Test basic inventory operations"""
    # Create a temporary file with test data
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write("# Inventory data\n")
        temp.write("samosa,10,2.50\n")
        temp.write("tacos,15,3.75\n")
        inventory_file = temp.name
    
    try:
        # Test reading inventory
        inventory = read_inventory(inventory_file)
        
        # Verify the read results
        assert 'samosa' in inventory, "Item 'samosa' not found in inventory"
        assert 'tacos' in inventory, "Item 'tacos' not found in inventory"
        
        # Check if values match
        assert inventory['samosa']['quantity'] == 10, "Quantity mismatch for samosa"
        assert inventory['samosa']['price'] == 2.50, "Price mismatch for samosa"
        assert inventory['tacos']['quantity'] == 15, "Quantity mismatch for tacos"
        assert inventory['tacos']['price'] == 3.75, "Price mismatch for tacos"
        
        # Test updating inventory
        update_inventory(inventory_file, "burger", 8, 5.25)
        
        # Verify the update
        updated_inventory = read_inventory(inventory_file)
        assert 'burger' in updated_inventory, "New item not added to inventory"
        assert updated_inventory['burger']['quantity'] == 8, "New item quantity incorrect"
        assert updated_inventory['burger']['price'] == 5.25, "New item price incorrect"
        
        TestUtils.yakshaAssert("test_inventory_operations", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_inventory_operations", False, "functional")
        raise e
    finally:
        os.remove(inventory_file)


def test_sales_and_feedback():
    """Test sales logging and feedback functions"""
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_sales:
        sales_file = temp_sales.name
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_feedback:
        feedback_file = temp_feedback.name
    
    try:
        # Test logging a sale
        log_sale(sales_file, "tacos", 3, 11.25)
        
        # Verify sale was logged correctly
        with open(sales_file, 'r') as file:
            content = file.readlines()
        
        # Check sales data format
        parts = content[0].strip().split(',')
        assert len(parts) == 4, "Sale record does not have 4 fields"
        assert "tacos" in parts, "Item name not found in sale record"
        assert "3" in parts, "Quantity not found in sale record"
        assert "11.25" in parts, "Total price not found in sale record"
        
        # Test saving customer feedback
        save_customer_feedback(feedback_file, "John Doe", 4, "Great food and quick service!")
        
        # Verify feedback was saved correctly
        with open(feedback_file, 'r') as file:
            content = file.read()
        
        assert "Customer: John Doe" in content, "Customer name not found"
        assert "Rating: 4/5" in content, "Rating not found"
        assert "Comments: Great food and quick service!" in content, "Comments not found"
        
        TestUtils.yakshaAssert("test_sales_and_feedback", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_sales_and_feedback", False, "functional")
        raise e
    finally:
        for file in [sales_file, feedback_file]:
            if os.path.exists(file):
                os.remove(file)


def test_sales_report():
    """Test sales report generation"""
    # Create a temporary file with test sales data
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write("timestamp,item_name,quantity,total_price\n")
        temp.write("2023-01-01 12:00:00,samosa,5,12.50\n")
        temp.write("2023-01-01 13:00:00,tacos,3,11.25\n")
        temp.write("2023-01-01 14:00:00,samosa,2,5.00\n")
        sales_file = temp.name
    
    try:
        # Test reading sales report
        report = read_sales_report(sales_file)
        
        # Verify the report data
        assert report['total_revenue'] > 0, "Total revenue should be greater than 0"
        assert report['items_sold'] > 0, "Items sold should be greater than 0"
        assert report['unique_items'] > 0, "Unique items should be greater than 0"
        assert report['best_seller'] is not None, "Best seller should not be None"
        assert 'samosa' in report['item_breakdown'], "Samosa should be in item breakdown"
        assert 'tacos' in report['item_breakdown'], "Tacos should be in item breakdown"
        
        TestUtils.yakshaAssert("test_sales_report", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_sales_report", False, "functional")
        raise e
    finally:
        os.remove(sales_file)


def test_file_operations_with_edge_formats():
    """Test handling of edge cases in file formats"""
    # Test inventory file with unusual spacing/formatting
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_inv:
        temp_inv.write("# Inventory with unusual formatting\n")
        temp_inv.write("samosa  ,  10,2.50\n")  # Extra spaces
        temp_inv.write("tacos,15  ,  3.75\n")   # More unusual spacing
        temp_inv.write("\n")                    # Empty line
        temp_inv.write("# Comment line\n")      # Comment in middle
        temp_inv.write("burger,8,5.25\n")       # Normal line after comment
        inventory_file = temp_inv.name
    
    try:
        # Test reading inventory with unusual formatting
        inventory = read_inventory(inventory_file)
        
        # Verify all items were correctly parsed - allowing for spaces in keys
        assert len(inventory) == 3, f"Expected 3 items in inventory, got {len(inventory)}"
        
        # Check if keys with or without spaces exist
        key_found = False
        for key in inventory.keys():
            if key.strip() == "samosa":
                key_found = True
                break
        assert key_found, "Failed to parse item with extra spaces"
        
        # Check tacos exists (either with or without spaces)
        key_found = False
        for key in inventory.keys():
            if key.strip() == "tacos":
                key_found = True
                break
        assert key_found, "Failed to parse item with unusual spacing"
        
        # Check burger exists
        key_found = False
        for key in inventory.keys():
            if key.strip() == "burger":
                key_found = True
                break
        assert key_found, "Failed to parse item after comment and empty line"
        
        TestUtils.yakshaAssert("test_file_operations_with_edge_formats", True, "boundary")
    except Exception as e:
        TestUtils.yakshaAssert("test_file_operations_with_edge_formats", False, "boundary")
        raise e
    finally:
        os.remove(inventory_file)