"""
Unit tests for the RetailOps CLI module, using subprocess to test CLI commands.
"""

import unittest
import os
import sys
import subprocess
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from retailops.cli import create_parser


class TestCreateParser(unittest.TestCase):
    """Test the argument parser construction."""

    def test_parser_created(self):
        """Test that parser is created."""
        parser = create_parser()
        self.assertIsNotNone(parser)

    def test_parser_has_commands(self):
        """Test parser has expected subcommands."""
        parser = create_parser()
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]
        self.assertTrue(len(subparsers_actions) > 0)
        subparser = subparsers_actions[0]
        for cmd in ["sales", "inventory", "customers", "returns",
                     "stores", "revenue", "report", "validate"]:
            self.assertIn(cmd, subparser.choices)


class TestCLISalesCommand(unittest.TestCase):
    """Test CLI sales command via subprocess."""

    def test_sales_help(self):
        """Test sales --help."""
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "sales", "--help"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())

    def test_sales_with_file(self):
        """Test sales with valid file."""
        sales_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "sales.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "sales", sales_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total Revenue", result.stdout)

    def test_sales_no_file(self):
        """Test sales without file."""
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "sales"],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertNotEqual(result.returncode, 0)


class TestCLIInventoryCommand(unittest.TestCase):
    """Test CLI inventory command via subprocess."""

    def test_inventory_with_file(self):
        """Test inventory with valid file."""
        inv_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "inventory.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "inventory", inv_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total Inventory Value", result.stdout)

    def test_inventory_bad_file(self):
        """Test inventory with non-existent file."""
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "inventory", "nonexistent.csv"],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 1)


class TestCLIReportCommand(unittest.TestCase):
    """Test CLI report command via subprocess."""

    def test_report_with_output(self):
        """Test report with output path."""
        output_path = os.path.join(
            os.path.dirname(__file__), "..", "reports", "test_report.md"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "report",
             "--output", output_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertTrue(os.path.exists(output_path))
        if os.path.exists(output_path):
            os.remove(output_path)

    def test_report_no_output(self):
        """Test report without output uses default path."""
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "report"],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        default_path = os.path.join(
            os.path.dirname(__file__), "..", "reports", "generated_report.md"
        )
        if os.path.exists(default_path):
            os.remove(default_path)


class TestCLIValidateCommand(unittest.TestCase):
    """Test CLI validate command via subprocess."""

    def test_validate_valid_file(self):
        """Test validate with valid CSV."""
        sales_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "sales.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "validate", sales_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)

    def test_validate_missing_file(self):
        """Test validate with missing file."""
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "validate", "missing.csv"],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 1)


class TestCLIReturnsCommand(unittest.TestCase):
    """Test CLI returns command."""

    def test_returns_with_files(self):
        """Test returns with valid files."""
        returns_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "returns.csv"
        )
        orders_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "orders.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "returns",
             returns_path, orders_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Return", result.stdout)


class TestCLIStoresCommand(unittest.TestCase):
    """Test CLI stores command."""

    def test_stores_with_files(self):
        """Test stores with valid files."""
        stores_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "stores.csv"
        )
        sales_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "sales.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "stores",
             stores_path, sales_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Store", result.stdout)


class TestCLIRevenueCommand(unittest.TestCase):
    """Test CLI revenue command."""

    def test_revenue_with_file(self):
        """Test revenue with valid file."""
        revenue_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "monthly_revenue.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "revenue", revenue_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Revenue", result.stdout)


class TestCLICustomersCommand(unittest.TestCase):
    """Test CLI customers command."""

    def test_customers_with_files(self):
        """Test customers with valid files."""
        customers_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "customers.csv"
        )
        orders_path = os.path.join(
            os.path.dirname(__file__), "..", "examples", "orders.csv"
        )
        result = subprocess.run(
            [sys.executable, "-m", "retailops.cli", "customers",
             customers_path, orders_path],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Customer", result.stdout)


if __name__ == "__main__":
    unittest.main()