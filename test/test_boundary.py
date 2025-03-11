import os
import tempfile
import pytest
from test.TestUtils import TestUtils
from street_food_vendor_management import read_inventory, update_inventory, read_sales_report, search_feedback


def test_inventory_boundary_cases():
    """Test boundary cases for inventory operations"""
    # Create a temporary file for testing empty inventory
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_empty:
        temp_empty.write("# Inventory - format: item_name,quantity,price\n")
        empty_file = temp_empty.name
    
    # Create a temporary file for testing large values
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_large:
        temp_large.write("# Inventory - format: item_name,quantity,price\n")
        temp_large.write("item1,999999,9999.99\n")  # Very large values
        large_file = temp_large.name
    
    # Create a temporary file for testing zero quantity
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_zero:
        temp_zero.write("# Inventory - format: item_name,quantity,price\n")
        temp_zero.write("item1,10,5.00\n")
        zero_file = temp_zero.name
    
    try:
        # Test empty inventory
        inventory = read_inventory(empty_file)
        assert isinstance(inventory, dict), "Result should be a dictionary"
        assert len(inventory) == 0, "Empty inventory should have 0 items"
        
        # Test large values
        inventory = read_inventory(large_file)
        assert 'item1' in inventory, "Item not found in inventory"
        assert inventory['item1']['quantity'] == 999999, "Large quantity not preserved"
        assert inventory['item1']['price'] == 9999.99, "Large price not preserved"
        
        # Test zero quantity update
        update_inventory(zero_file, "item1", 0, 5.00)
        inventory = read_inventory(zero_file)
        assert 'item1' in inventory, "Item not found in inventory"
        assert inventory['item1']['quantity'] == 0, "Quantity should be zero"
        
        TestUtils.yakshaAssert("test_inventory_boundary_cases", True, "boundary")
    except Exception as e:
        TestUtils.yakshaAssert("test_inventory_boundary_cases", False, "boundary")
        raise e
    finally:
        for file in [empty_file, large_file, zero_file]:
            if os.path.exists(file):
                os.remove(file)


def test_reporting_and_search_boundary_cases():
    """Test boundary cases for reporting and search operations"""
    # Create a temporary file for empty sales report
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_sales:
        temp_sales.write("timestamp,item_name,quantity,total_price\n")
        sales_file = temp_sales.name
    
    # Create empty feedback file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_empty_feedback:
        empty_feedback_file = temp_empty_feedback.name
    
    # Create feedback file with content but no matches
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_feedback:
        temp_feedback.write("===== FEEDBACK: 2023-01-01 12:00:00 =====\n")
        temp_feedback.write("Customer: John Doe\n")
        temp_feedback.write("Rating: 4/5\n")
        temp_feedback.write("Comments: Great food and service!\n\n")
        feedback_file = temp_feedback.name
    
    try:
        # Test empty sales report
        report = read_sales_report(sales_file)
        assert report['total_revenue'] == 0, "Total revenue should be 0"
        assert report['items_sold'] == 0, "Items sold should be 0"
        assert report['unique_items'] == 0, "Unique items should be 0"
        assert report['best_seller'] is None, "Best seller should be None"
        
        # Test searching empty feedback
        results = search_feedback(empty_feedback_file, "test")
        assert isinstance(results, list), "Result should be a list"
        assert len(results) == 0, "Empty feedback should return empty list"
        
        # Test searching with no matches
        results = search_feedback(feedback_file, "terrible")
        assert isinstance(results, list), "Result should be a list"
        assert len(results) == 0, "No matches should return empty list"
        
        TestUtils.yakshaAssert("test_reporting_and_search_boundary_cases", True, "boundary")
    except Exception as e:
        TestUtils.yakshaAssert("test_reporting_and_search_boundary_cases", False, "boundary")
        raise e
    finally:
        for file in [sales_file, empty_feedback_file, feedback_file]:
            if os.path.exists(file):
                os.remove(file)