"""
Unit tests for the RetailOps customer analytics module.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retailops.customers import (
    calculate_customer_order_counts,
    calculate_customer_revenue,
    assign_customer_segment,
    build_customer_profiles,
    summarize_segments,
    find_top_customers,
    build_customer_summary,
)
from retailops.data_loader import read_csv_rows


class TestCalculateCustomerOrderCounts(unittest.TestCase):
    """Test calculate_customer_order_counts."""

    def test_empty_orders(self):
        """Test with empty orders."""
        customers = [{"customer_id": "1", "name": "Alice"}]
        result = calculate_customer_order_counts(customers, [])
        self.assertEqual(result["1"], 0)

    def test_single_customer(self):
        """Test with single customer orders."""
        customers = [{"customer_id": "1", "name": "Alice"}]
        orders = [
            {"customer_id": "1", "unit_price": "10.00", "quantity": "1"},
            {"customer_id": "1", "unit_price": "20.00", "quantity": "2"},
        ]
        result = calculate_customer_order_counts(customers, orders)
        self.assertEqual(result["1"], 2)

    def test_multiple_customers(self):
        """Test with multiple customers."""
        customers = [{"customer_id": "1", "name": "A"},
                     {"customer_id": "2", "name": "B"}]
        orders = [
            {"customer_id": "1", "unit_price": "10.00", "quantity": "1"},
            {"customer_id": "2", "unit_price": "20.00", "quantity": "1"},
            {"customer_id": "1", "unit_price": "15.00", "quantity": "1"},
        ]
        result = calculate_customer_order_counts(customers, orders)
        self.assertEqual(result["1"], 2)
        self.assertEqual(result["2"], 1)


class TestCalculateCustomerRevenue(unittest.TestCase):
    """Test calculate_customer_revenue."""

    def test_empty_orders(self):
        """Test with empty orders."""
        customers = [{"customer_id": "1", "name": "Alice"}]
        result = calculate_customer_revenue(customers, [])
        self.assertAlmostEqual(result["1"], 0.0)

    def test_with_orders(self):
        """Test with orders."""
        customers = [{"customer_id": "1", "name": "Alice"}]
        orders = [
            {"customer_id": "1", "unit_price": "10.00", "quantity": "2"},
            {"customer_id": "1", "unit_price": "5.00", "quantity": "3"},
        ]
        result = calculate_customer_revenue(customers, orders)
        self.assertAlmostEqual(result["1"], 35.0)


class TestAssignCustomerSegment(unittest.TestCase):
    """Test assign_customer_segment."""

    def test_vip_revenue(self):
        """Test VIP by revenue."""
        self.assertEqual(assign_customer_segment(1000, 5), "VIP")

    def test_vip_orders(self):
        """Test VIP by orders."""
        self.assertEqual(assign_customer_segment(500, 10), "VIP")

    def test_loyal_revenue(self):
        """Test LOYAL by revenue."""
        self.assertEqual(assign_customer_segment(500, 4), "LOYAL")

    def test_loyal_orders(self):
        """Test LOYAL by orders."""
        self.assertEqual(assign_customer_segment(100, 5), "LOYAL")

    def test_active(self):
        """Test ACTIVE customer."""
        self.assertEqual(assign_customer_segment(50, 1), "ACTIVE")

    def test_new(self):
        """Test NEW customer."""
        self.assertEqual(assign_customer_segment(0, 0), "NEW")


class TestBuildCustomerProfiles(unittest.TestCase):
    """Test build_customer_profiles."""

    def test_empty_customers(self):
        """Test with empty customers."""
        self.assertEqual(build_customer_profiles([], []), [])

    def test_with_data(self):
        """Test with sample data."""
        customers = [
            {"customer_id": "1", "name": "Alice", "email": "a@test.com",
             "signup_date": "2024-01-01", "city": "NYC"},
        ]
        orders = [
            {"customer_id": "1", "unit_price": "100.00", "quantity": "2"},
        ]
        profiles = build_customer_profiles(customers, orders)
        self.assertEqual(len(profiles), 1)
        profile = profiles[0]
        self.assertEqual(profile["name"], "Alice")
        self.assertAlmostEqual(profile["total_revenue"], 200.0)
        self.assertEqual(profile["order_count"], 1)
        self.assertEqual(profile["segment"], "ACTIVE")


class TestSummarizeSegments(unittest.TestCase):
    """Test summarize_segments."""

    def test_empty_profiles(self):
        """Test with empty profiles."""
        summary = summarize_segments([])
        for seg in ["VIP", "LOYAL", "ACTIVE", "NEW"]:
            self.assertEqual(summary[seg], 0)

    def test_with_profiles(self):
        """Test with profiles."""
        profiles = [
            {"segment": "VIP"},
            {"segment": "VIP"},
            {"segment": "LOYAL"},
            {"segment": "NEW"},
        ]
        summary = summarize_segments(profiles)
        self.assertEqual(summary["VIP"], 2)
        self.assertEqual(summary["LOYAL"], 1)
        self.assertEqual(summary["ACTIVE"], 0)
        self.assertEqual(summary["NEW"], 1)


class TestFindTopCustomers(unittest.TestCase):
    """Test find_top_customers."""

    def test_empty_profiles(self):
        """Test with empty profiles."""
        self.assertEqual(find_top_customers([]), [])

    def test_with_profiles(self):
        """Test with sample profiles."""
        profiles = [
            {"name": "A", "total_revenue": 100, "order_count": 1, "segment": "ACTIVE"},
            {"name": "B", "total_revenue": 500, "order_count": 10, "segment": "VIP"},
            {"name": "C", "total_revenue": 200, "order_count": 3, "segment": "LOYAL"},
        ]
        top = find_top_customers(profiles, limit=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]["name"], "B")


class TestBuildCustomerSummary(unittest.TestCase):
    """Test build_customer_summary."""

    def test_empty_data(self):
        """Test with empty data."""
        summary = build_customer_summary([], [])
        self.assertEqual(summary["total_customers"], 0)

    def test_with_data(self):
        """Test with sample data."""
        customers = [
            {"customer_id": "1", "name": "Alice", "email": "a@test.com",
             "signup_date": "2024-01-01", "city": "NYC"},
        ]
        orders = [
            {"customer_id": "1", "unit_price": "100.00", "quantity": "1"},
        ]
        summary = build_customer_summary(customers, orders)
        self.assertEqual(summary["total_customers"], 1)
        self.assertIn("segment_summary", summary)
        self.assertIn("profiles", summary)


class TestLoadCustomerData(unittest.TestCase):
    """Test loading customer data from CSV."""

    def test_customers_file_exists(self):
        """Test that customers.csv exists."""
        filepath = os.path.join(
            os.path.dirname(__file__), "..", "examples", "customers.csv"
        )
        rows = read_csv_rows(filepath)
        self.assertGreater(len(rows), 0)

    def test_orders_file_exists(self):
        """Test that orders.csv exists."""
        filepath = os.path.join(
            os.path.dirname(__file__), "..", "examples", "orders.csv"
        )
        rows = read_csv_rows(filepath)
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()