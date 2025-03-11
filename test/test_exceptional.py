import os
import tempfile
import pytest
from test.TestUtils import TestUtils
from street_food_vendor_management import read_inventory, update_inventory, log_sale, save_customer_feedback, read_sales_report


def test_file_and_format_exceptions():
    """Test file not found and invalid format exceptions"""
    # Generate a non-existent file path
    non_existent_file = "non_existent_file_" + os.urandom(8).hex() + ".txt"
    
    # Create a temporary file with invalid inventory format
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_inv:
        temp_inv.write("# Inventory data\n")
        temp_inv.write("This line has an invalid format\n")
        invalid_inv_file = temp_inv.name
    
    # Create a temporary file with invalid sales CSV format
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_sales:
        temp_sales.write("timestamp,item_name,quantity,total_price\n")
        temp_sales.write("2023-01-01 12:00:00,item1,not-a-number,5.00\n")
        invalid_sales_file = temp_sales.name
    
    try:
        # Test file not found
        with pytest.raises(FileNotFoundError):
            read_inventory(non_existent_file)
        
        # Test invalid inventory format
        with pytest.raises(ValueError):
            read_inventory(invalid_inv_file)
        
        # Test invalid sales CSV format
        with pytest.raises(ValueError):
            read_sales_report(invalid_sales_file)
        
        TestUtils.yakshaAssert("test_file_and_format_exceptions", True, "exceptional")
    except Exception as e:
        TestUtils.yakshaAssert("test_file_and_format_exceptions", False, "exceptional")
        raise e
    finally:
        for file in [invalid_inv_file, invalid_sales_file]:
            if os.path.exists(file):
                os.remove(file)


def test_invalid_input_exceptions():
    """Test invalid input parameter exceptions"""
    # Create a temporary file with valid inventory data
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_inv:
        temp_inv.write("# Inventory - format: item_name,quantity,price\n")
        temp_inv.write("item1,10,5.00\n")
        inv_file = temp_inv.name
    
    # Create a temporary file for sale logging
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_sale:
        sale_file = temp_sale.name
    
    # Create a temporary file for feedback
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_feedback:
        feedback_file = temp_feedback.name
    
    try:
        # Test invalid quantity type
        with pytest.raises(ValueError):
            update_inventory(inv_file, "item1", "not-a-number", 5.00)
        
        # Test invalid price type
        with pytest.raises(ValueError):
            update_inventory(inv_file, "item1", 10, "not-a-price")
        
        # Test invalid rating range (too high)
        with pytest.raises(ValueError):
            save_customer_feedback(feedback_file, "John Doe", 6, "Great food!")
        
        # Test invalid rating range (too low)
        with pytest.raises(ValueError):
            save_customer_feedback(feedback_file, "John Doe", 0, "Great food!")
        
        # Test negative sale quantity
        with pytest.raises(ValueError):
            log_sale(sale_file, "item1", -1, 5.00)
        
        # Test negative sale price
        with pytest.raises(ValueError):
            log_sale(sale_file, "item1", 1, -5.00)
        
        TestUtils.yakshaAssert("test_invalid_input_exceptions", True, "exceptional")
    except Exception as e:
        TestUtils.yakshaAssert("test_invalid_input_exceptions", False, "exceptional")
        raise e
    finally:
        for file in [inv_file, sale_file, feedback_file]:
            if os.path.exists(file):
                os.remove(file)