"""
Unit tests for the RetailOps sales analytics module.
Tests each function in the sales module with various inputs.
"""

import unittest
import os
import sys
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retailops.sales import (
    calculate_order_revenue,
    calculate_total_revenue,
    calculate_total_quantity,
    group_revenue_by_product,
    group_revenue_by_category,
    group_revenue_by_store,
    find_top_group,
    calculate_average_order_revenue,
    build_sales_summary,
    print_sales_summary,
)


class TestCalculateOrderRevenue(unittest.TestCase):
    """Tests for calculate_order_revenue."""

    def test_standard_order(self):
        """Test a normal order with total_amount."""
        order = {"total_amount": "21.0"}
        result = calculate_order_revenue(order)
        self.assertAlmostEqual(result, 21.0)

    def test_large_values(self):
        """Test order with large price and quantity."""
        order = {"total_amount": "999999.0"}
        result = calculate_order_revenue(order)
        self.assertAlmostEqual(result, 999999.0)

    def test_zero_quantity(self):
        """Test order with zero amount."""
        order = {"total_amount": "0"}
        result = calculate_order_revenue(order)
        self.assertAlmostEqual(result, 0.0)

    def test_missing_amount(self):
        """Test order missing total_amount."""
        order = {"product": "Widget"}
        result = calculate_order_revenue(order)
        self.assertAlmostEqual(result, 0.0)

    def test_invalid_amount(self):
        """Test order with non-numeric amount."""
        order = {"total_amount": "N/A"}
        result = calculate_order_revenue(order)
        self.assertAlmostEqual(result, 0.0)


class TestCalculateTotalRevenue(unittest.TestCase):
    """Tests for calculate_total_revenue."""

    def test_empty_list(self):
        """Test empty orders list."""
        self.assertAlmostEqual(calculate_total_revenue([]), 0.0)

    def test_single_order(self):
        """Test single order."""
        orders = [{"total_amount": "100.0"}]
        self.assertAlmostEqual(calculate_total_revenue(orders), 100.0)

    def test_multiple_orders(self):
        """Test multiple orders."""
        orders = [
            {"total_amount": "20.0"},
            {"total_amount": "35.0"},
        ]
        self.assertAlmostEqual(calculate_total_revenue(orders), 55.0)


class TestCalculateTotalQuantity(unittest.TestCase):
    """Tests for calculate_total_quantity."""

    def test_empty_list(self):
        """Test empty orders list."""
        self.assertEqual(calculate_total_quantity([]), 0)

    def test_single_order(self):
        """Test single order."""
        orders = [{"quantity": "5"}]
        self.assertEqual(calculate_total_quantity(orders), 5)

    def test_multiple_orders(self):
        """Test multiple orders."""
        orders = [{"quantity": "3"}, {"quantity": "7"}]
        self.assertEqual(calculate_total_quantity(orders), 10)

    def test_missing_quantity(self):
        """Test order with missing quantity."""
        orders = [{"product": "Widget"}]
        self.assertEqual(calculate_total_quantity(orders), 0)


class TestGroupRevenueByProduct(unittest.TestCase):
    """Tests for group_revenue_by_product."""

    def test_empty_list(self):
        """Test empty orders."""
        self.assertEqual(group_revenue_by_product([]), {})

    def test_single_product(self):
        """Test single product."""
        orders = [{"product_name": "Widget", "total_amount": "20.0"}]
        result = group_revenue_by_product(orders)
        self.assertAlmostEqual(result["Widget"], 20.0)

    def test_multiple_products(self):
        """Test multiple products."""
        orders = [
            {"product_name": "A", "total_amount": "10.0"},
            {"product_name": "B", "total_amount": "15.0"},
            {"product_name": "A", "total_amount": "5.0"},
        ]
        result = group_revenue_by_product(orders)
        self.assertAlmostEqual(result["A"], 15.0)
        self.assertAlmostEqual(result["B"], 15.0)


class TestGroupRevenueByCategory(unittest.TestCase):
    """Tests for group_revenue_by_category."""

    def test_empty_list(self):
        """Test empty orders."""
        self.assertEqual(group_revenue_by_category([]), {})

    def test_single_category(self):
        """Test single category."""
        orders = [{"category": "Electronics", "total_amount": "100.0"}]
        result = group_revenue_by_category(orders)
        self.assertAlmostEqual(result["Electronics"], 100.0)

    def test_multiple_categories(self):
        """Test multiple categories."""
        orders = [
            {"category": "A", "total_amount": "10.0"},
            {"category": "B", "total_amount": "20.0"},
        ]
        result = group_revenue_by_category(orders)
        self.assertAlmostEqual(result["A"], 10.0)
        self.assertAlmostEqual(result["B"], 20.0)


class TestGroupRevenueByStore(unittest.TestCase):
    """Tests for group_revenue_by_store."""

    def test_empty_list(self):
        """Test empty orders."""
        self.assertEqual(group_revenue_by_store([]), {})

    def test_single_store(self):
        """Test single store."""
        orders = [{"store_id": "1", "total_amount": "100.0"}]
        result = group_revenue_by_store(orders)
        self.assertAlmostEqual(result["1"], 100.0)

    def test_multiple_stores(self):
        """Test multiple stores."""
        orders = [
            {"store_id": "1", "total_amount": "50.0"},
            {"store_id": "2", "total_amount": "75.0"},
        ]
        result = group_revenue_by_store(orders)
        self.assertAlmostEqual(result["1"], 50.0)
        self.assertAlmostEqual(result["2"], 75.0)


class TestFindTopGroup(unittest.TestCase):
    """Tests for find_top_group."""

    def test_empty_dict(self):
        """Test empty grouped data."""
        self.assertEqual(find_top_group({}), [])

    def test_top_items(self):
        """Test with sample data."""
        data = {"A": 100, "B": 50, "C": 25}
        result = find_top_group(data)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ("A", 100))

    def test_limit_param(self):
        """Test with custom limit."""
        data = {"A": 100, "B": 50, "C": 25}
        result = find_top_group(data, limit=2)
        self.assertEqual(len(result), 2)


class TestCalculateAverageOrderRevenue(unittest.TestCase):
    """Tests for calculate_average_order_revenue."""

    def test_empty_list(self):
        """Test empty orders list."""
        self.assertAlmostEqual(calculate_average_order_revenue([]), 0.0)

    def test_single_order(self):
        """Test single order."""
        orders = [{"total_amount": "100.0"}]
        self.assertAlmostEqual(calculate_average_order_revenue(orders), 100.0)

    def test_multiple_orders(self):
        """Test multiple orders."""
        orders = [
            {"total_amount": "20.0"},
            {"total_amount": "30.0"},
        ]
        self.assertAlmostEqual(calculate_average_order_revenue(orders), 25.0)


class TestBuildSalesSummary(unittest.TestCase):
    """Tests for build_sales_summary."""

    def test_empty_orders(self):
        """Test with empty orders."""
        summary = build_sales_summary([])
        self.assertAlmostEqual(summary["total_revenue"], 0.0)
        self.assertEqual(summary["total_quantity"], 0)
        self.assertEqual(summary["order_count"], 0)

    def test_with_orders(self):
        """Test with sample orders."""
        orders = [
            {"total_amount": "20.0", "quantity": "2",
             "product_name": "A", "category": "Cat1", "store_id": "1"},
            {"total_amount": "30.0", "quantity": "3",
             "product_name": "B", "category": "Cat2", "store_id": "2"},
        ]
        summary = build_sales_summary(orders)
        self.assertAlmostEqual(summary["total_revenue"], 50.0)
        self.assertEqual(summary["total_quantity"], 5)
        self.assertEqual(summary["order_count"], 2)
        self.assertAlmostEqual(summary["average_revenue"], 25.0)


class TestLoadSalesData(unittest.TestCase):
    """Tests for loading sales CSV data."""

    def test_sales_file_exists(self):
        """Test that sales.csv exists and is not empty."""
        sales_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "sales.csv"
        )
        self.assertTrue(os.path.exists(sales_path))
        with open(sales_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertTrue(len(rows) > 0)

    def test_sales_has_columns(self):
        """Test sales.csv has required columns."""
        sales_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "sales.csv"
        )
        with open(sales_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertIn("total_amount", rows[0])


class TestPrintSalesSummary(unittest.TestCase):
    """Tests for print_sales_summary."""

    def test_print(self):
        """Test print doesn't crash."""
        summary = build_sales_summary([])
        try:
            print_sales_summary(summary)
        except Exception:
            self.fail("print_sales_summary raised an exception")


if __name__ == "__main__":
    unittest.main()