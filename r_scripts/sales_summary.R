# sales_summary.R
# RetailOps CLI Suite - Sales Analysis Script
# Reads sales.csv and outputs comprehensive sales statistics
#
# Usage: Rscript r_scripts/sales_summary.R
#        Rscript r_scripts/sales_summary.R examples/sales.csv

# ============================================================
# Configuration and Setup
# ============================================================

# Determine file path from command line argument or use default
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 1) {
  sales_file <- args[1]
} else {
  sales_file <- file.path("examples", "sales.csv")
}

# Output file for detailed results
output_file <- file.path("reports", "r_sales_summary.txt")

# ============================================================
# Helper Functions
# ============================================================

#' Read CSV file safely with error handling
#' 
#' @param file_path Path to the CSV file
#' @return data.frame or stops execution on error
read_sales_csv <- function(file_path) {
  if (!file.exists(file_path)) {
    cat("ERROR: File not found:", file_path, "\n")
    quit(status = 1)
  }
  
  data <- tryCatch(
    read.csv(file_path, stringsAsFactors = FALSE),
    error = function(e) {
      cat("ERROR: Failed to read CSV:", e$message, "\n")
      quit(status = 1)
    }
  )
  
  if (nrow(data) == 0) {
    cat("ERROR: File is empty:", file_path, "\n")
    quit(status = 1)
  }
  
  cat("Successfully loaded", nrow(data), "records from", file_path, "\n")
  return(data)
}

#' Convert a column to numeric, coercing NAs
#'
#' @param x Vector of values
#' @return Numeric vector
safe_as_numeric <- function(x) {
  result <- suppressWarnings(as.numeric(x))
  result[is.na(result)] <- 0
  return(result)
}

#' Format a number as currency
#'
#' @param value Numeric value
#' @return Character string with dollar format
format_currency <- function(value) {
  return(sprintf("$%.2f", value))
}

#' Format a number with commas
#'
#' @param value Numeric value
#' @return Character string
format_number <- function(value) {
  return(format(round(value, 0), big.mark = ",", scientific = FALSE))
}

#' Print a section header
#'
#' @param title Section title
print_header <- function(title) {
  cat("\n", paste(rep("=", 60), collapse = ""), "\n", sep = "")
  cat("  ", title, "\n", sep = "")
  cat(paste(rep("=", 60), collapse = ""), "\n", sep = "")
}

#' Print a sub-header
#'
#' @param title Sub-section title
print_subheader <- function(title) {
  cat("\n--- ", title, " ---\n", sep = "")
}

#' Write a line to the output file
#'
#' @param con File connection
#' @param line Text line
write_output_line <- function(con, line) {
  writeLines(line, con)
}

# ============================================================
# Data Loading
# ============================================================

cat("\n============================================================\n")
cat("  R Sales Summary Report\n")
cat("============================================================\n\n")

sales_data <- read_sales_csv(sales_file)
cat("Columns:", paste(names(sales_data), collapse = ", "), "\n")
cat("Rows:", nrow(sales_data), "\n")

# ============================================================
# Data Preparation
# ============================================================

# Normalize column names to lowercase for case-insensitive matching
names(sales_data) <- tolower(names(sales_data))

# Identify required columns with flexible naming
col_total_amount <- grep("total_amount|total|amount|revenue|price", 
                          names(sales_data), value = TRUE)[1]
col_quantity <- grep("quantity|qty|count|units", 
                      names(sales_data), value = TRUE)[1]
col_product <- grep("product_name|product|item_name|item", 
                     names(sales_data), value = TRUE)[1]
col_category <- grep("category|product_category|type|group", 
                      names(sales_data), value = TRUE)[1]
col_store <- grep("store_name|store|location|branch", 
                   names(sales_data), value = TRUE)[1]
col_date <- grep("date|sale_date|transaction_date|order_date", 
                  names(sales_data), value = TRUE)[1]

cat("Mapped columns:\n")
cat("  Amount column:", col_total_amount, "\n")
cat("  Quantity column:", col_quantity, "\n")
cat("  Product column:", col_product, "\n")
cat("  Category column:", col_category, "\n")
cat("  Store column:", col_store, "\n")
cat("  Date column:", col_date, "\n\n")

# Convert amount and quantity to numeric
if (!is.null(col_total_amount)) {
  sales_data[[col_total_amount]] <- safe_as_numeric(sales_data[[col_total_amount]])
}
if (!is.null(col_quantity)) {
  sales_data[[col_quantity]] <- safe_as_numeric(sales_data[[col_quantity]])
}

# ============================================================
# Basic Statistics
# ============================================================

print_header("BASIC STATISTICS")

total_revenue <- if (!is.null(col_total_amount)) sum(sales_data[[col_total_amount]], na.rm = TRUE) else 0
total_quantity <- if (!is.null(col_quantity)) sum(sales_data[[col_quantity]], na.rm = TRUE) else 0
order_count <- nrow(sales_data)

cat("  Total Revenue:     ", format_currency(total_revenue), "\n", sep = "")
cat("  Total Quantity:    ", format_number(total_quantity), "\n", sep = "")
cat("  Order Count:       ", format_number(order_count), "\n", sep = "")
cat("  Average Order Rev: ", format_currency(total_revenue / order_count), "\n", sep = "")
cat("  Min Order Amount:  ", format_currency(min(sales_data[[col_total_amount]])), "\n", sep = "")
cat("  Max Order Amount:  ", format_currency(max(sales_data[[col_total_amount]])), "\n", sep = "")
cat("  Median Order Amt:  ", format_currency(median(sales_data[[col_total_amount]])), "\n", sep = "")

# ============================================================
# Revenue by Product
# ============================================================

print_header("REVENUE BY PRODUCT")

if (!is.null(col_product) && !is.null(col_total_amount)) {
  product_revenue <- aggregate(
    sales_data[[col_total_amount]],
    by = list(Product = sales_data[[col_product]]),
    FUN = sum,
    na.rm = TRUE
  )
  names(product_revenue) <- c("Product", "Revenue")
  product_revenue <- product_revenue[order(product_revenue$Revenue, decreasing = TRUE), ]
  product_revenue$Percent <- round(product_revenue$Revenue / total_revenue * 100, 1)
  
  cat(sprintf("  %-30s %12s  %s\n", "Product", "Revenue", "%"))
  cat("  ", paste(rep("-", 50), collapse = ""), "\n", sep = "")
  
  for (i in 1:min(10, nrow(product_revenue))) {
    cat(sprintf("  %-30s %12s  %.1f%%\n",
        substr(product_revenue$Product[i], 1, 28),
        format_currency(product_revenue$Revenue[i]),
        product_revenue$Percent[i]))
  }
  
  if (nrow(product_revenue) > 10) {
    others <- sum(product_revenue$Revenue[11:nrow(product_revenue)])
    others_pct <- sum(product_revenue$Percent[11:nrow(product_revenue)])
    cat(sprintf("  %-30s %12s  %.1f%%\n", "Other Products", format_currency(others), others_pct))
  }
} else {
  cat("  No product column available for grouping.\n")
}

# ============================================================
# Revenue by Category
# ============================================================

print_header("REVENUE BY CATEGORY")

if (!is.null(col_category) && !is.null(col_total_amount)) {
  category_revenue <- aggregate(
    sales_data[[col_total_amount]],
    by = list(Category = sales_data[[col_category]]),
    FUN = sum,
    na.rm = TRUE
  )
  names(category_revenue) <- c("Category", "Revenue")
  category_revenue <- category_revenue[order(category_revenue$Revenue, decreasing = TRUE), ]
  category_revenue$Percent <- round(category_revenue$Revenue / total_revenue * 100, 1)
  
  cat(sprintf("  %-25s %12s  %s\n", "Category", "Revenue", "%"))
  cat("  ", paste(rep("-", 45), collapse = ""), "\n", sep = "")
  
  for (i in 1:nrow(category_revenue)) {
    cat(sprintf("  %-25s %12s  %.1f%%\n",
        substr(category_revenue$Category[i], 1, 23),
        format_currency(category_revenue$Revenue[i]),
        category_revenue$Percent[i]))
  }
} else {
  cat("  No category column available for grouping.\n")
}

# ============================================================
# Revenue by Store
# ============================================================

print_header("REVENUE BY STORE")

if (!is.null(col_store) && !is.null(col_total_amount)) {
  store_revenue <- aggregate(
    sales_data[[col_total_amount]],
    by = list(Store = sales_data[[col_store]]),
    FUN = sum,
    na.rm = TRUE
  )
  names(store_revenue) <- c("Store", "Revenue")
  store_revenue <- store_revenue[order(store_revenue$Revenue, decreasing = TRUE), ]
  store_revenue$Percent <- round(store_revenue$Revenue / total_revenue * 100, 1)
  
  cat(sprintf("  %-25s %12s  %s\n", "Store", "Revenue", "%"))
  cat("  ", paste(rep("-", 45), collapse = ""), "\n", sep = "")
  
  for (i in 1:nrow(store_revenue)) {
    cat(sprintf("  %-25s %12s  %.1f%%\n",
        substr(store_revenue$Store[i], 1, 23),
        format_currency(store_revenue$Revenue[i]),
        store_revenue$Percent[i]))
  }
} else {
  cat("  No store column available for grouping.\n")
}

# ============================================================
# Monthly Revenue Trend
# ============================================================

print_header("MONTHLY REVENUE TREND")

if (!is.null(col_date) && !is.null(col_total_amount)) {
  # Convert date column to Date format
  dates <- as.Date(sales_data[[col_date]], format = "%Y-%m-%d")
  months <- format(dates, "%Y-%m")
  
  monthly_revenue <- aggregate(
    sales_data[[col_total_amount]],
    by = list(Month = months),
    FUN = sum,
    na.rm = TRUE
  )
  names(monthly_revenue) <- c("Month", "Revenue")
  monthly_revenue <- monthly_revenue[order(monthly_revenue$Month), ]
  
  cat(sprintf("  %-10s %12s\n", "Month", "Revenue"))
  cat("  ", paste(rep("-", 25), collapse = ""), "\n", sep = "")
  
  for (i in 1:nrow(monthly_revenue)) {
    cat(sprintf("  %-10s %12s\n",
        monthly_revenue$Month[i],
        format_currency(monthly_revenue$Revenue[i])))
  }
  
  avg_monthly <- mean(monthly_revenue$Revenue, na.rm = TRUE)
  best_month <- monthly_revenue[which.max(monthly_revenue$Revenue), ]
  worst_month <- monthly_revenue[which.min(monthly_revenue$Revenue), ]
  
  cat("\n")
  cat("  Average Monthly: ", format_currency(avg_monthly), "\n", sep = "")
  cat("  Best Month:      ", best_month$Month, " (", format_currency(best_month$Revenue), ")\n", sep = "")
  cat("  Worst Month:     ", worst_month$Month, " (", format_currency(worst_month$Revenue), ")\n", sep = "")
} else {
  cat("  No date column available for trend analysis.\n")
}

# ============================================================
# Quantity Analysis
# ============================================================

print_header("QUANTITY ANALYSIS")

if (!is.null(col_quantity)) {
  qty_summary <- summary(sales_data[[col_quantity]])
  cat("  Min Quantity:     ", format_number(min(sales_data[[col_quantity]])), "\n")
  cat("  Max Quantity:     ", format_number(max(sales_data[[col_quantity]])), "\n")
  cat("  Median Quantity:  ", format_number(median(sales_data[[col_quantity]])), "\n")
  cat("  Mean Quantity:    ", format_number(mean(sales_data[[col_quantity]])), "\n")
  cat("  Total Quantity:   ", format_number(total_quantity), "\n")
} else {
  cat("  No quantity column available.\n")
}

# ============================================================
# Price Point Analysis (if both amount and quantity available)
# ============================================================

print_header("PRICE POINT ANALYSIS")

if (!is.null(col_total_amount) && !is.null(col_quantity) && total_quantity > 0) {
  avg_price <- total_revenue / total_quantity
  cat("  Average Price per Unit: ", format_currency(avg_price), "\n", sep = "")
  
  item_prices <- sales_data[[col_total_amount]] / sales_data[[col_quantity]]
  item_prices <- item_prices[is.finite(item_prices)]
  
  cat("  Min Unit Price:         ", format_currency(min(item_prices)), "\n", sep = "")
  cat("  Max Unit Price:         ", format_currency(max(item_prices)), "\n", sep = "")
  cat("  Median Unit Price:      ", format_currency(median(item_prices)), "\n", sep = "")
} else {
  cat("  Insufficient data for price analysis.\n")
}

# ============================================================
# Summary
# ============================================================

print_header("SUMMARY")

cat("  File:            ", sales_file, "\n")
cat("  Total Orders:    ", format_number(order_count), "\n")
cat("  Total Revenue:   ", format_currency(total_revenue), "\n")
cat("  Total Quantity:  ", format_number(total_quantity), "\n")
cat("  Avg Order Value: ", format_currency(total_revenue / order_count), "\n")

if (exists("product_revenue") && nrow(product_revenue) > 0) {
  top_product <- product_revenue[1, ]
  cat("  Top Product:     ", top_product$Product, " (", format_currency(top_product$Revenue), ")\n", sep = "")
}

if (exists("category_revenue") && nrow(category_revenue) > 0) {
  top_category <- category_revenue[1, ]
  cat("  Top Category:    ", top_category$Category, " (", format_currency(top_category$Revenue), ")\n", sep = "")
}

if (exists("store_revenue") && nrow(store_revenue) > 0) {
  top_store <- store_revenue[1, ]
  cat("  Top Store:       ", top_store$Store, " (", format_currency(top_store$Revenue), ")\n", sep = "")
}

# Save output to file
if (!dir.exists(dirname(output_file))) {
  dir.create(dirname(output_file), recursive = TRUE)
}

sink(output_file)
cat("R Sales Summary Report\n")
cat("======================\n\n")
cat("File:", sales_file, "\n")
cat("Total Orders:", format_number(order_count), "\n")
cat("Total Revenue:", format_currency(total_revenue), "\n")
cat("Total Quantity:", format_number(total_quantity), "\n")
cat("Average Order Revenue:", format_currency(total_revenue / order_count), "\n")
sink()

cat("\nReport saved to:", output_file, "\n")
cat("Analysis complete.\n")