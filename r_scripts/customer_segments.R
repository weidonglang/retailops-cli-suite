#!/usr/bin/env Rscript
#
# customer_segments.R
#
# Customer Segmentation Analysis Script for RetailOps CLI Suite
#
# Analyzes customer data and order history to segment customers into
# VIP, Loyal, Active, and New tiers based on purchase behavior.
#
# Usage:
#   Rscript r_scripts/customer_segments.R examples/customers.csv examples/orders.csv
#
# Outputs:
#   - Customer segmentation summary
#   - Segment distribution
#   - Top customers by revenue
#   - Customer profile details
#
# This script uses only base R (no external packages).

# ---- Command-Line Argument Parsing ----
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  cat("ERROR: Missing arguments.\n")
  cat("Usage: Rscript r_scripts/customer_segments.R <customers_csv> <orders_csv>\n")
  quit(status = 1)
}

customers_file <- args[1]
orders_file <- args[2]

# ---- Helper Functions ----

# Read a CSV file with error handling
read_csv_safe <- function(filepath) {
  if (!file.exists(filepath)) {
    cat(sprintf("ERROR: File not found: %s\n", filepath))
    quit(status = 1)
  }
  data <- read.csv(filepath, stringsAsFactors = FALSE)
  if (nrow(data) == 0) {
    cat(sprintf("ERROR: Empty file: %s\n", filepath))
    quit(status = 1)
  }
  cat(sprintf("Successfully loaded %d records from %s\n", nrow(data), filepath))
  cat(sprintf("Columns: %s\n", paste(names(data), collapse = ", ")))
  cat(sprintf("Rows: %d\n\n", nrow(data)))
  return(data)
}

# Format money as currency string
format_money <- function(value) {
  sprintf("$%.2f", value)
}

# Format percentage
format_percent <- function(value, digits = 1) {
  sprintf("%.1f%%", value * 100)
}

# Print a section header
print_header <- function(title) {
  cat(sprintf("\n%s\n", paste(rep("=", 60), collapse = "")))
  cat(sprintf("  %s\n", title))
  cat(sprintf("%s\n\n", paste(rep("=", 60), collapse = "")))
}

# Print a sub-header
print_subheader <- function(title) {
  cat(sprintf("\n  --- %s ---\n\n", title))
}

# Print a separator line
print_separator <- function() {
  cat(sprintf("%s\n", paste(rep("-", 60), collapse = "")))
}

# ---- Load Data ----
cat("============================================================\n")
cat("  R Customer Segmentation Report\n")
cat("============================================================\n\n")

customers <- read_csv_safe(customers_file)
orders <- read_csv_safe(orders_file)

# ---- Data Validation ----
required_customer_cols <- c("customer_id", "name")
required_order_cols <- c("order_id", "customer_id", "quantity", "unit_price")

for (col in required_customer_cols) {
  if (!(col %in% names(customers))) {
    cat(sprintf("ERROR: Missing required column '%s' in customers file.\n", col))
    quit(status = 1)
  }
}

for (col in required_order_cols) {
  if (!(col %in% names(orders))) {
    cat(sprintf("ERROR: Missing required column '%s' in orders file.\n", col))
    quit(status = 1)
  }
}

# ---- Data Cleaning ----
# Convert customer_id to character for joining
customers$customer_id <- as.character(customers$customer_id)
orders$customer_id <- as.character(orders$customer_id)

# Ensure numeric columns
orders$quantity <- as.numeric(orders$quantity)
orders$unit_price <- as.numeric(orders$unit_price)

# Remove rows with NA values
orders <- orders[!is.na(orders$quantity) & !is.na(orders$unit_price), ]
customers <- customers[!is.na(customers$customer_id), ]

# Calculate order revenue
orders$revenue <- orders$quantity * orders$unit_price

cat(sprintf("Cleaned data: %d customers, %d orders\n\n", nrow(customers), nrow(orders)))

# ---- Calculate Customer Metrics ----
# Aggregate order data per customer
customer_order_counts <- aggregate(order_id ~ customer_id, data = orders, FUN = length)
names(customer_order_counts) <- c("customer_id", "order_count")

customer_revenue <- aggregate(revenue ~ customer_id, data = orders, FUN = sum)
names(customer_revenue) <- c("customer_id", "total_revenue")

# Merge metrics
customer_metrics <- merge(customer_order_counts, customer_revenue, by = "customer_id", all = TRUE)
customer_metrics$order_count[is.na(customer_metrics$order_count)] <- 0
customer_metrics$total_revenue[is.na(customer_metrics$total_revenue)] <- 0

# Merge with customer details
customer_profiles <- merge(customers, customer_metrics, by = "customer_id", all.x = TRUE)
customer_profiles$order_count[is.na(customer_profiles$order_count)] <- 0
customer_profiles$total_revenue[is.na(customer_profiles$total_revenue)] <- 0

# Calculate average revenue per order
customer_profiles$avg_revenue_per_order <- 0
has_orders <- customer_profiles$order_count > 0
customer_profiles$avg_revenue_per_order[has_orders] <-
  customer_profiles$total_revenue[has_orders] / customer_profiles$order_count[has_orders]

# ---- Customer Segmentation ----
#
# Segmentation Rules:
#   VIP:   revenue >= 1000 OR orders >= 10
#   LOYAL: revenue >= 500 OR orders >= 5
#   ACTIVE: revenue > 0
#   NEW:   revenue == 0
#
assign_segment <- function(total_revenue, order_count) {
  if (total_revenue >= 1000 || order_count >= 10) {
    return("VIP")
  } else if (total_revenue >= 500 || order_count >= 5) {
    return("LOYAL")
  } else if (total_revenue > 0) {
    return("ACTIVE")
  } else {
    return("NEW")
  }
}

customer_profiles$segment <- mapply(assign_segment,
  customer_profiles$total_revenue,
  customer_profiles$order_count)

# ---- Print Customer Segmentation Report ----
print_header("CUSTOMER SEGMENTATION REPORT")

# Basic Statistics
cat(sprintf("Total Customers:      %d\n", nrow(customers)))
cat(sprintf("Customers with Orders: %d\n", sum(customer_profiles$order_count > 0)))
cat(sprintf("Total Orders:         %d\n", nrow(orders)))
cat(sprintf("Total Revenue:        %s\n", format_money(sum(orders$revenue))))
cat(sprintf("Avg Orders/Customer:  %.2f\n", mean(customer_profiles$order_count)))
cat(sprintf("Avg Revenue/Customer: %s\n", format_money(mean(customer_profiles$total_revenue))))
cat(sprintf("Max Orders:           %d\n", max(customer_profiles$order_count)))
cat(sprintf("Max Revenue:          %s\n\n", format_money(max(customer_profiles$total_revenue))))

# ---- Segment Distribution ----
print_header("SEGMENT DISTRIBUTION")
segment_counts <- table(factor(customer_profiles$segment, levels = c("VIP", "LOYAL", "ACTIVE", "NEW")))
segment_order <- c("VIP", "LOYAL", "ACTIVE", "NEW")
segment_pct <- prop.table(segment_counts)

cat(sprintf("%-15s %10s %15s\n", "Segment", "Count", "Percentage"))
print_separator()
for (seg in names(segment_counts)) {
  cnt <- segment_counts[seg]
  pct <- segment_pct[seg]
  cat(sprintf("%-15s %10d %14s\n", seg, cnt, format_percent(pct, 1)))
}

# ---- Segment Revenue Statistics ----
print_header("SEGMENT REVENUE STATISTICS")
cat(sprintf("%-15s %15s %15s %15s\n", "Segment", "Total Revenue", "Avg/Customer", "Avg/Order"))
print_separator()
for (seg in segment_order) {
  seg_profiles <- customer_profiles[customer_profiles$segment == seg, ]
  total_rev <- sum(seg_profiles$total_revenue)
  avg_cust <- mean(seg_profiles$total_revenue)
  seg_orders <- orders[orders$customer_id %in% seg_profiles$customer_id, ]
  avg_order <- mean(seg_orders$revenue)
  cat(sprintf("%-15s %15s %15s %15s\n",
    seg,
    format_money(total_rev),
    format_money(avg_cust),
    format_money(avg_order)))
}

# ---- Top Customers ----
print_header("TOP 10 CUSTOMERS BY REVENUE")
sorted_customers <- customer_profiles[order(-customer_profiles$total_revenue), ]
top_10 <- head(sorted_customers, 10)
cat(sprintf("%-5s %-25s %-10s %15s %15s %-10s\n",
  "ID", "Name", "City", "Orders", "Revenue", "Segment"))
print_separator()
for (i in 1:nrow(top_10)) {
  cat(sprintf("%-5s %-25s %-10s %10d %15s %-10s\n",
    top_10$customer_id[i],
    substr(top_10$name[i], 1, 24),
    substr(top_10$city[i], 1, 9),
    top_10$order_count[i],
    format_money(top_10$total_revenue[i]),
    top_10$segment[i]))
}

# ---- Top Customers by Orders ----
print_header("TOP 10 CUSTOMERS BY ORDER COUNT")
sorted_by_orders <- customer_profiles[order(-customer_profiles$order_count), ]
top_by_orders <- head(sorted_by_orders, 10)
cat(sprintf("%-5s %-25s %-10s %10s %15s %-10s\n",
  "ID", "Name", "City", "Orders", "Revenue", "Segment"))
print_separator()
for (i in 1:nrow(top_by_orders)) {
  cat(sprintf("%-5s %-25s %-10s %10d %15s %-10s\n",
    top_by_orders$customer_id[i],
    substr(top_by_orders$name[i], 1, 24),
    substr(top_by_orders$city[i], 1, 9),
    top_by_orders$order_count[i],
    format_money(top_by_orders$total_revenue[i]),
    top_by_orders$segment[i]))
}

# ---- City Distribution ----
print_header("CUSTOMERS BY CITY")
city_counts <- table(customers$city)
sorted_cities <- sort(city_counts, decreasing = TRUE)
cat(sprintf("%-25s %10s %10s\n", "City", "Count", "Pct"))
print_separator()
for (i in seq_along(sorted_cities)) {
  city <- names(sorted_cities)[i]
  cnt <- sorted_cities[i]
  pct <- cnt / nrow(customers)
  cat(sprintf("%-25s %10d %10s\n", city, cnt, format_percent(pct, 1)))
}

# ---- Segment Detailed Profiles ----
print_header("SEGMENT DETAILED PROFILES")

for (seg in segment_order) {
  print_subheader(seg)
  seg_profiles <- customer_profiles[customer_profiles$segment == seg, ]
  cat(sprintf("  Count:      %d customers\n", nrow(seg_profiles)))
  if (nrow(seg_profiles) > 0) {
    cat(sprintf("  Total Rev:  %s\n", format_money(sum(seg_profiles$total_revenue))))
    cat(sprintf("  Avg Rev:    %s\n", format_money(mean(seg_profiles$total_revenue))))
    cat(sprintf("  Avg Orders: %.2f\n", mean(seg_profiles$order_count)))
    cat(sprintf("  Customers:\n"))
    for (j in 1:min(5, nrow(seg_profiles))) {
      row <- seg_profiles[j, ]
      cat(sprintf("    - %s (%s): %d orders, %s\n",
        row$name, row$city, row$order_count, format_money(row$total_revenue)))
    }
  }
  cat("\n")
}

# ---- New vs Returning Analysis ----
print_header("NEW VS RETURNING CUSTOMERS")
new_customers <- customer_profiles[customer_profiles$segment == "NEW", ]
returning_customers <- customer_profiles[customer_profiles$segment != "NEW", ]
cat(sprintf("New Customers:       %d (%.1f%%)\n",
  nrow(new_customers), nrow(new_customers) / nrow(customer_profiles) * 100))
cat(sprintf("Returning Customers: %d (%.1f%%)\n",
  nrow(returning_customers), nrow(returning_customers) / nrow(customer_profiles) * 100))
cat(sprintf("New Customer Rev:    %s\n", format_money(sum(new_customers$total_revenue))))
cat(sprintf("Returning Cust Rev:  %s\n", format_money(sum(returning_customers$total_revenue))))

# ---- Summary ----
print_header("FINAL SUMMARY")
cat(sprintf("  File Analyzed:          %s\n", customers_file))
cat(sprintf("  Orders File:            %s\n", orders_file))
cat(sprintf("  Total Customers:        %d\n", nrow(customer_profiles)))
cat(sprintf("  Total Orders:           %d\n", nrow(orders)))
cat(sprintf("  Total Revenue:          %s\n", format_money(sum(customer_profiles$total_revenue))))
cat(sprintf("  VIP Customers:          %d\n", segment_counts["VIP"]))
cat(sprintf("  Loyal Customers:        %d\n", segment_counts["LOYAL"]))
cat(sprintf("  Active Customers:       %d\n", segment_counts["ACTIVE"]))
cat(sprintf("  New Customers:          %d\n", segment_counts["NEW"]))
cat(sprintf("  Avg Revenue/Customer:   %s\n", format_money(mean(customer_profiles$total_revenue))))
cat(sprintf("  Med Revenue/Customer:   %s\n", format_money(median(customer_profiles$total_revenue))))
cat(sprintf("  Avg Orders/Customer:    %.2f\n", mean(customer_profiles$order_count)))
cat(sprintf("  Top Segment:            %s\n", names(which.max(segment_counts))))
cat("\nAnalysis complete.\n")