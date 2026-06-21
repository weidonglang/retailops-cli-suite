#!/usr/bin/env Rscript
#
# test_r_scripts.R
#
# Test runner for R analysis scripts in RetailOps CLI Suite.
#
# Tests the 4 R scripts by running them with example data and
# verifying their output contains expected results.
#
# Usage:
#   Rscript tests/test_r_scripts.R
#
# This script uses only base R (no external packages).

# ---- Test Framework Functions ----
test_passed <- 0
test_failed <- 0
test_errors <- c()

assert_equal <- function(expected, actual, msg = "") {
  result <- isTRUE(all.equal(expected, actual))
  if (result) {
    test_passed <<- test_passed + 1
    cat(sprintf("  [PASS] %s\n", msg))
  } else {
    test_failed <<- test_failed + 1
    err_msg <- sprintf("  [FAIL] %s: expected '%s', got '%s'",
      msg, paste(expected, collapse = ","), paste(actual, collapse = ","))
    cat(err_msg, "\n")
    test_errors <<- c(test_errors, err_msg)
  }
  invisible(result)
}

assert_true <- function(condition, msg = "") {
  result <- isTRUE(condition)
  if (result) {
    test_passed <<- test_passed + 1
    cat(sprintf("  [PASS] %s\n", msg))
  } else {
    test_failed <<- test_failed + 1
    err_msg <- sprintf("  [FAIL] %s: expected TRUE", msg)
    cat(err_msg, "\n")
    test_errors <<- c(test_errors, err_msg)
  }
  invisible(result)
}

assert_contains <- function(haystack, needle, msg = "") {
  result <- grepl(needle, haystack, fixed = TRUE)
  if (result) {
    test_passed <<- test_passed + 1
    cat(sprintf("  [PASS] %s\n", msg))
  } else {
    test_failed <<- test_failed + 1
    err_msg <- sprintf("  [FAIL] %s: output does not contain '%s'", msg, needle)
    cat(err_msg, "\n")
    test_errors <<- c(test_errors, err_msg)
  }
  invisible(result)
}

print_test_summary <- function() {
  total <- test_passed + test_failed
  cat("\n============================================================\n")
  cat(sprintf("  R Script Test Results\n"))
  cat(sprintf("  Total:  %d\n", total))
  cat(sprintf("  Passed: %d\n", test_passed))
  cat(sprintf("  Failed: %d\n", test_failed))
  cat("============================================================\n")
  if (test_failed > 0) {
    cat("\nFAILURES:\n")
    for (err in test_errors) {
      cat(err, "\n")
    }
    quit(status = 1)
  } else {
    cat("\nAll R script tests passed.\n")
  }
}

# Helper to capture output of an Rscript command
capture_script_output <- function(script_path, args = character(0)) {
  cmd <- sprintf("Rscript %s %s 2>&1",
    shQuote(script_path),
    paste(shQuote(args), collapse = " "))
  result <- tryCatch({
    output <- system(cmd, intern = TRUE)
    paste(output, collapse = "\n")
  }, error = function(e) {
    return(paste("ERROR:", e$message))
  })
  return(result)
}

cat("============================================================\n")
cat("  R Script Test Runner for RetailOps CLI Suite\n")
cat("============================================================\n\n")

# ---- Setup: Verify file existence ----
cat("--- Setup: Checking file existence ---\n")

base_dir <- getwd()
scripts_dir <- file.path(base_dir, "r_scripts")
examples_dir <- file.path(base_dir, "examples")

# Check that all required R scripts exist
required_scripts <- c(
  "sales_summary.R",
  "inventory_summary.R",
  "customer_segments.R",
  "revenue_forecast.R"
)
for (script in required_scripts) {
  script_path <- file.path(scripts_dir, script)
  assert_true(file.exists(script_path),
    sprintf("R script exists: %s", script))
}

# Check that all required example files exist
required_examples <- c(
  "sales.csv",
  "inventory.csv",
  "customers.csv",
  "orders.csv",
  "monthly_revenue.csv"
)
for (ex in required_examples) {
  ex_path <- file.path(examples_dir, ex)
  assert_true(file.exists(ex_path),
    sprintf("Example CSV exists: %s", ex))
}

cat("\n--- Testing sales_summary.R ---\n")

output <- capture_script_output(
  file.path(scripts_dir, "sales_summary.R"),
  file.path(examples_dir, "sales.csv"))

assert_contains(output, "Sales Summary Report",
  "sales_summary.R: Contains report header")
assert_contains(output, "Total Revenue",
  "sales_summary.R: Contains revenue section")
assert_contains(output, "REVENUE BY PRODUCT",
  "sales_summary.R: Contains top products section")
assert_contains(output, "REVENUE BY CATEGORY",
  "sales_summary.R: Contains top categories section")
assert_contains(output, "REVENUE BY STORE",
  "sales_summary.R: Contains top stores section")
assert_contains(output, "$",
  "sales_summary.R: Contains monetary values")
assert_contains(output, "Product",
  "sales_summary.R: Contains product column")

cat("\n--- Testing inventory_summary.R ---\n")

output <- capture_script_output(
  file.path(scripts_dir, "inventory_summary.R"),
  file.path(examples_dir, "inventory.csv"))

assert_contains(output, "Inventory Summary",
  "inventory_summary.R: Contains report header")
assert_contains(output, "Total Items",
  "inventory_summary.R: Contains total items count")
assert_contains(output, "Total Stock",
  "inventory_summary.R: Contains total stock count")
assert_contains(output, "Total Inventory Value",
  "inventory_summary.R: Contains inventory value")
assert_contains(output, "Reorder",
  "inventory_summary.R: Contains reorder suggestions")
assert_contains(output, "STOCK STATUS",
  "inventory_summary.R: Contains stock status indicators")
assert_contains(output, "Out of Stock",
  "inventory_summary.R: Contains out of stock indicator")

cat("\n--- Testing customer_segments.R ---\n")

output <- capture_script_output(
  file.path(scripts_dir, "customer_segments.R"),
  c(file.path(examples_dir, "customers.csv"),
    file.path(examples_dir, "orders.csv")))

assert_contains(output, "Customer Segmentation",
  "customer_segments.R: Contains report header")
assert_contains(output, "Total Customers",
  "customer_segments.R: Contains total customers")
assert_contains(output, "Total Revenue",
  "customer_segments.R: Contains total revenue")
assert_contains(output, "SEGMENT DISTRIBUTION",
  "customer_segments.R: Contains segment distribution")
assert_contains(output, "ACTIVE",
  "customer_segments.R: Contains active segment")
assert_contains(output, "NEW",
  "customer_segments.R: Contains new segment")
assert_contains(output, "TOP 10 CUSTOMERS",
  "customer_segments.R: Contains top customers list")
assert_contains(output, "VIP",
  "customer_segments.R: Contains VIP segment header")

cat("\n--- Testing revenue_forecast.R ---\n")

output <- capture_script_output(
  file.path(scripts_dir, "revenue_forecast.R"),
  file.path(examples_dir, "monthly_revenue.csv"))

assert_contains(output, "Revenue Forecast",
  "revenue_forecast.R: Contains report header")
assert_contains(output, "Total Revenue",
  "revenue_forecast.R: Contains total revenue")
assert_contains(output, "Average Monthly",
  "revenue_forecast.R: Contains average monthly revenue")
assert_contains(output, "Best",
  "revenue_forecast.R: Contains best month")
assert_contains(output, "Worst",
  "revenue_forecast.R: Contains worst month")
assert_contains(output, "Growth Rate",
  "revenue_forecast.R: Contains growth rate analysis")
assert_contains(output, "MOVING AVERAGE",
  "revenue_forecast.R: Contains moving average analysis")
assert_contains(output, "Forecast",
  "revenue_forecast.R: Contains forecast section")

cat("\n--- Testing error handling ---\n")

# Test that missing file produces error
output <- capture_script_output(
  file.path(scripts_dir, "sales_summary.R"),
  "nonexistent.csv")
assert_contains(output, "ERROR",
  "sales_summary.R: Reports error for missing file")

# Test missing argument
output <- capture_script_output(
  file.path(scripts_dir, "inventory_summary.R"),
  character(0))
assert_contains(output, "ERROR",
  "inventory_summary.R: Reports error for missing arguments")

# Test customer_segments with missing orders file
output <- capture_script_output(
  file.path(scripts_dir, "customer_segments.R"),
  c(file.path(examples_dir, "customers.csv"), "nonexistent.csv"))
assert_contains(output, "ERROR",
  "customer_segments.R: Reports error for missing orders file")

# Test revenue_forecast with missing file
output <- capture_script_output(
  file.path(scripts_dir, "revenue_forecast.R"),
  "nonexistent.csv")
assert_contains(output, "ERROR",
  "revenue_forecast.R: Reports error for missing file")

cat("\n--- Testing data integrity via R ---\n")

# Load data directly and validate
sales <- read.csv(file.path(examples_dir, "sales.csv"), stringsAsFactors = FALSE)
assert_true(nrow(sales) > 0, "sales.csv has rows")
assert_true("product_id" %in% names(sales), "sales.csv has product_id")
assert_true("quantity" %in% names(sales), "sales.csv has quantity")
assert_true("unit_price" %in% names(sales), "sales.csv has unit_price")
assert_true(all(sales$quantity > 0), "All sales quantities are positive")
assert_true(all(sales$unit_price > 0), "All sales unit prices are positive")

inventory <- read.csv(file.path(examples_dir, "inventory.csv"), stringsAsFactors = FALSE)
assert_true(nrow(inventory) > 0, "inventory.csv has rows")
assert_true("current_stock" %in% names(inventory), "inventory.csv has current_stock")
assert_true("reorder_point" %in% names(inventory), "inventory.csv has reorder_point")
assert_true(all(inventory$current_stock >= 0), "All stock quantities are non-negative")

customers <- read.csv(file.path(examples_dir, "customers.csv"), stringsAsFactors = FALSE)
assert_true(nrow(customers) > 0, "customers.csv has rows")
assert_true("customer_id" %in% names(customers), "customers.csv has customer_id")
assert_true("name" %in% names(customers), "customers.csv has name")

orders <- read.csv(file.path(examples_dir, "orders.csv"), stringsAsFactors = FALSE)
assert_true(nrow(orders) > 0, "orders.csv has rows")
assert_true("order_id" %in% names(orders), "orders.csv has order_id")
assert_true("customer_id" %in% names(orders), "orders.csv has customer_id")
assert_true("store_id" %in% names(orders), "orders.csv has store_id")
assert_true("quantity" %in% names(orders), "orders.csv has quantity")
assert_true("unit_price" %in% names(orders), "orders.csv has unit_price")

# Verify customer IDs match between customers and orders
customer_ids <- unique(customers$customer_id)
order_customer_ids <- unique(orders$customer_id)
matching_ids <- intersect(customer_ids, order_customer_ids)
assert_true(length(matching_ids) > 0,
  "At least some customers have orders in the data")

# Basic math verification
order_revenues <- orders$quantity * orders$unit_price
total_revenue <- sum(order_revenues)
assert_true(total_revenue > 0, "Total revenue is positive")

# Verify monthly revenue data
monthly_rev <- read.csv(file.path(examples_dir, "monthly_revenue.csv"),
  stringsAsFactors = FALSE)
assert_true(nrow(monthly_rev) > 0, "monthly_revenue.csv has rows")
assert_true("total_revenue" %in% names(monthly_rev),
  "monthly_revenue.csv has total_revenue")
assert_true("month" %in% names(monthly_rev),
  "monthly_revenue.csv has month")
assert_true("year" %in% names(monthly_rev),
  "monthly_revenue.csv has year")
assert_true(all(monthly_rev$total_revenue > 0),
  "All monthly revenues are positive")

# Check for expected number of assertions
total_assertions <- test_passed + test_failed
cat(sprintf("\nTotal assertions executed: %d\n", total_assertions))
assert_true(total_assertions >= 20,
  sprintf("At least 20 assertions executed (got %d)", total_assertions))

# ---- Print Summary ----
print_test_summary()