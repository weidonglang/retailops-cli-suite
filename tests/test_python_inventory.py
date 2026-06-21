"""
Unit tests for the RetailOps inventory analytics module.
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retailops.inventory import (
    calculate_inventory_value,
    calculate_reorder_quantity,
    calculate_days_of_stock_left,
    assign_stock_status,
    enrich_inventory_item,
    enrich_inventory_items,
    summarize_inventory_by_category,
    find_top_reorder_item,
    find_top_inventory_category,
    build_inventory_summary,
    OUT_OF_STOCK,
    LOW_STOCK,
    OK,
)


class TestCalculateInventoryValue(unittest.TestCase):
    """Test calculate_inventory_value."""

    def test_standard_item(self):
        """Test normal item."""
        item = {"current_stock": "10", "unit_cost": "5.50"}
        result = calculate_inventory_value(item)
        self.assertAlmostEqual(result, 55.0)

    def test_zero_stock(self):
        """Test zero stock."""
        item = {"current_stock": "0", "unit_cost": "5.00"}
        result = calculate_inventory_value(item)
        self.assertAlmostEqual(result, 0.0)

    def test_missing_fields(self):
        """Test missing fields."""
        item = {"product": "Widget"}
        result = calculate_inventory_value(item)
        self.assertAlmostEqual(result, 0.0)


class TestCalculateReorderQuantity(unittest.TestCase):
    """Test calculate_reorder_quantity."""

    def test_low_stock(self):
        """Test with low stock."""
        item = {"current_stock": "3", "reorder_point": "10"}
        result = calculate_reorder_quantity(item)
        self.assertEqual(result, 17)

    def test_adequate_stock(self):
        """Test with adequate stock (reorder_point * 2 - stock < reorder_point)."""
        item = {"current_stock": "50", "reorder_point": "10"}
        result = calculate_reorder_quantity(item)
        # suggested = 20 - 50 = -30 -> max(-30, 10) = 10
        self.assertEqual(result, 10)

    def test_exact_reorder(self):
        """Test when stock equals reorder_point."""
        item = {"current_stock": "10", "reorder_point": "10"}
        result = calculate_reorder_quantity(item)
        # suggested = 20 - 10 = 10 -> max(10, 10) = 10
        self.assertEqual(result, 10)

    def test_zero_reorder_point(self):
        """Test zero reorder point."""
        item = {"current_stock": "5", "reorder_point": "0"}
        result = calculate_reorder_quantity(item)
        # suggested = 0 - 5 = -5 -> max(-5, 0) = 0
        self.assertEqual(result, 0)


class TestCalculateDaysOfStockLeft(unittest.TestCase):
    """Test calculate_days_of_stock_left."""

    def test_default_demand(self):
        """Test with default demand (5)."""
        item = {"current_stock": "30"}
        result = calculate_days_of_stock_left(item)
        self.assertEqual(result, 6)

    def test_custom_demand(self):
        """Test with custom demand."""
        item = {"current_stock": "100"}
        result = calculate_days_of_stock_left(item, daily_demand=10)
        self.assertEqual(result, 10)

    def test_zero_stock(self):
        """Test zero stock."""
        item = {"current_stock": "0"}
        result = calculate_days_of_stock_left(item)
        self.assertEqual(result, 0)


class TestAssignStockStatus(unittest.TestCase):
    """Test assign_stock_status."""

    def test_out_of_stock(self):
        """Test OUT_OF_STOCK.
        OUT_OF_STOCK: current_stock == 0"""
        item = {"current_stock": "0", "reorder_point": "5"}
        self.assertEqual(assign_stock_status(item), OUT_OF_STOCK)

    def test_low_stock(self):
        """Test LOW_STOCK.
        LOW_STOCK: current_stock <= reorder_point
        stock=3, reorder_point=5 -> LOW_STOCK"""
        item = {"current_stock": "3", "reorder_point": "5"}
        self.assertEqual(assign_stock_status(item), LOW_STOCK)

    def test_ok(self):
        """Test OK.
        OK: current_stock > reorder_point
        stock=10, reorder_point=5 -> OK"""
        item = {"current_stock": "10", "reorder_point": "5"}
        self.assertEqual(assign_stock_status(item), OK)

    def test_missing_fields(self):
        """Test missing fields defaults to 0 stock -> OUT_OF_STOCK."""
        item = {}
        self.assertEqual(assign_stock_status(item), OUT_OF_STOCK)


class TestEnrichInventoryItem(unittest.TestCase):
    """Test enrich_inventory_item."""

    def test_full_enrichment(self):
        """Test enrich adds all calculated fields."""
        item = {
            "product_name": "Widget",
            "current_stock": "20",
            "unit_cost": "2.50",
            "reorder_point": "5",
            "category": "Tools",
        }
        enriched = enrich_inventory_item(item)
        self.assertAlmostEqual(enriched["inventory_value"], 50.0)
        self.assertEqual(enriched["reorder_quantity"], 5)
        self.assertEqual(enriched["days_of_stock"], 4)
        self.assertEqual(enriched["stock_status"], OK)


class TestEnrichInventoryItems(unittest.TestCase):
    """Test enrich_inventory_items."""

    def test_empty_list(self):
        """Test empty list."""
        self.assertEqual(enrich_inventory_items([]), [])

    def test_multiple_items(self):
        """Test multiple items."""
        items = [
            {"product_name": "A", "current_stock": "0", "unit_cost": "1.0",
             "reorder_point": "5", "category": "C1"},
            {"product_name": "B", "current_stock": "10", "unit_cost": "2.0",
             "reorder_point": "5", "category": "C2"},
        ]
        enriched = enrich_inventory_items(items)
        self.assertEqual(len(enriched), 2)
        self.assertEqual(enriched[0]["stock_status"], OUT_OF_STOCK)
        self.assertEqual(enriched[1]["stock_status"], OK)


class TestSummarizeInventoryByCategory(unittest.TestCase):
    """Test summarize_inventory_by_category."""

    def test_empty_list(self):
        """Test empty list."""
        self.assertEqual(summarize_inventory_by_category([]), {})

    def test_single_item(self):
        """Test single item."""
        items = [
            {"product_name": "A", "current_stock": "10", "unit_cost": "5.0",
             "reorder_point": "3", "category": "Tools"},
        ]
        enrich = enrich_inventory_items(items)
        summary = summarize_inventory_by_category(enrich)
        self.assertIn("Tools", summary)
        self.assertAlmostEqual(summary["Tools"]["total_value"], 50.0)
        self.assertEqual(summary["Tools"]["item_count"], 1)


class TestBuildInventorySummary(unittest.TestCase):
    """Test build_inventory_summary."""

    def test_empty_list(self):
        """Test empty list."""
        summary = build_inventory_summary([])
        self.assertEqual(summary["total_items"], 0)

    def test_with_items(self):
        """Test with items."""
        items = [
            {"product_name": "A", "current_stock": "10", "unit_cost": "5.0",
             "reorder_point": "3", "category": "Tools"},
        ]
        summary = build_inventory_summary(items)
        self.assertEqual(summary["total_items"], 1)
        self.assertAlmostEqual(summary["total_value"], 50.0)
        self.assertEqual(summary["low_stock_count"], 0)
        self.assertEqual(summary["out_of_stock_count"], 0)
        self.assertIn("category_summary", summary)


class TestLoadInventoryFile(unittest.TestCase):
    """Test loading inventory CSV."""

    def test_inventory_file_exists(self):
        """Test that inventory.csv exists."""
        filepath = os.path.join(
            os.path.dirname(__file__), "..", "examples", "inventory.csv"
        )
        from retailops.data_loader import read_csv_rows
        rows = read_csv_rows(filepath)
        self.assertGreater(len(rows), 0)


if __name__ == "__main__":
    unittest.main()