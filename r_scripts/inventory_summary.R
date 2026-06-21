# inventory_summary.R
# RetailOps CLI Suite - Inventory Analysis Script
# Reads inventory.csv and outputs comprehensive inventory statistics
#
# Usage: Rscript r_scripts/inventory_summary.R
#        Rscript r_scripts/inventory_summary.R examples/inventory.csv

# ============================================================
# Configuration and Setup
# ============================================================

# Determine file path from command line argument or use default
args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 1) {
  inventory_file <- args[1]
} else {
  inventory_file <- file.path("examples", "inventory.csv")
}

# Output file for detailed results
output_file <- file.path("reports", "r_inventory_summary.txt")

# ============================================================
# Helper Functions
# ============================================================

#' Read CSV file safely with error handling
#'
#' @param file_path Path to the CSV file
#' @return data.frame or stops execution on error
read_inventory_csv <- function(file_path) {
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

#' Convert a column to numeric, coercing NAs to 0
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
#' @return Character string
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

# ============================================================
# Data Loading
# ============================================================

cat("\n============================================================\n")
cat("  R Inventory Summary Report\n")
cat("============================================================\n\n")

inventory_data <- read_inventory_csv(inventory_file)
cat("Columns:", paste(names(inventory_data), collapse = ", "), "\n")
cat("Rows:", nrow(inventory_data), "\n\n")

# ============================================================
# Data Preparation
# ============================================================

# Normalize column names to lowercase
names(inventory_data) <- tolower(names(inventory_data))

# Identify required columns with flexible matching
col_product <- grep("product_name|product|item_name|item|sku", 
                     names(inventory_data), value = TRUE)[1]
col_category <- grep("category|product_category|type|group|department", 
                      names(inventory_data), value = TRUE)[1]
col_stock <- grep("stock_quantity|quantity|stock|qty_on_hand|on_hand", 
                   names(inventory_data), value = TRUE)[1]
col_price <- grep("unit_price|price|cost|cost_per_unit", 
                   names(inventory_data), value = TRUE)[1]
col_reorder <- grep("reorder_point|reorder|min_stock|threshold", 
                     names(inventory_data), value = TRUE)[1]
col_supplier <- grep("supplier|vendor|manufacturer", 
                      names(inventory_data), value = TRUE)[1]

cat("Mapped columns:\n")
cat("  Product column:   ", col_product, "\n")
cat("  Category column:  ", col_category, "\n")
cat("  Stock column:     ", col_stock, "\n")
cat("  Price column:     ", col_price, "\n")
cat("  Reorder column:   ", col_reorder, "\n")
cat("  Supplier column:  ", col_supplier, "\n\n")

# Convert numeric columns
if (!is.null(col_stock)) {
  inventory_data[[col_stock]] <- safe_as_numeric(inventory_data[[col_stock]])
}
if (!is.null(col_price)) {
  inventory_data[[col_price]] <- safe_as_numeric(inventory_data[[col_price]])
}
if (!is.null(col_reorder)) {
  inventory_data[[col_reorder]] <- safe_as_numeric(inventory_data[[col_reorder]])
}

# ============================================================
# Basic Inventory Statistics
# ============================================================

print_header("BASIC INVENTORY STATISTICS")

item_count <- nrow(inventory_data)
total_stock <- if (!is.null(col_stock)) sum(inventory_data[[col_stock]], na.rm = TRUE) else 0
avg_stock <- if (!is.null(col_stock)) mean(inventory_data[[col_stock]], na.rm = TRUE) else 0

cat("  Total Items:       ", format_number(item_count), "\n")
cat("  Total Stock Units: ", format_number(total_stock), "\n")
cat("  Avg Stock/Item:    ", format(round(avg_stock, 1), big.mark = ",", scientific = FALSE), "\n")

if (!is.null(col_stock)) {
  cat("  Min Stock:         ", format_number(min(inventory_data[[col_stock]])), "\n")
  cat("  Max Stock:         ", format_number(max(inventory_data[[col_stock]])), "\n")
  cat("  Median Stock:      ", format_number(median(inventory_data[[col_stock]])), "\n")
}

# ============================================================
# Inventory Value Analysis
# ============================================================

print_header("INVENTORY VALUE ANALYSIS")

if (!is.null(col_stock) && !is.null(col_price)) {
  inventory_data$value <- inventory_data[[col_stock]] * inventory_data[[col_price]]
  total_value <- sum(inventory_data$value, na.rm = TRUE)
  avg_value <- mean(inventory_data$value, na.rm = TRUE)
  max_value_item <- inventory_data[which.max(inventory_data$value), ]
  
  cat("  Total Inventory Value: ", format_currency(total_value), "\n")
  cat("  Average Item Value:    ", format_currency(avg_value), "\n")
  cat("  Max Item Value:        ", format_currency(max(inventory_data$value)), "\n")
  
  if (!is.null(col_product)) {
    max_product <- max_value_item[[col_product]]
    cat("  Highest Value Item:    ", max_product, "\n")
  }
  
  cat("\n  Top 10 Items by Value:\n")
  cat(sprintf("  %-30s %10s %12s %12s\n", "Product", "Stock", "Price", "Value"))
  cat("  ", paste(rep("-", 68), collapse = ""), "\n", sep = "")
  
  top_value <- inventory_data[order(inventory_data$value, decreasing = TRUE), ]
  for (i in 1:min(10, nrow(top_value))) {
    prod_name <- if (!is.null(col_product)) substr(top_value[[col_product]][i], 1, 28) else paste("Item", i)
    cat(sprintf("  %-30s %10s %12s %12s\n",
        prod_name,
        format_number(top_value[[col_stock]][i]),
        format_currency(top_value[[col_price]][i]),
        format_currency(top_value$value[i])))
  }
} else {
  cat("  Insufficient data for value analysis.\n")
}

# ============================================================
# Stock Status Classification
# ============================================================

print_header("STOCK STATUS ANALYSIS")

if (!is.null(col_stock)) {
  # Define stock status
  out_of_stock <- inventory_data[inventory_data[[col_stock]] == 0, ]
  low_stock_count <- 0
  ok_stock_count <- 0
  
  if (!is.null(col_reorder)) {
    low_stock <- inventory_data[
      inventory_data[[col_stock]] > 0 & 
      inventory_data[[col_stock]] <= inventory_data[[col_reorder]], 
    ]
    ok_stock <- inventory_data[inventory_data[[col_stock]] > inventory_data[[col_reorder]], ]
    low_stock_count <- nrow(low_stock)
    ok_stock_count <- nrow(ok_stock)
  } else {
    # If no reorder point, use 10 as default threshold
    low_stock <- inventory_data[
      inventory_data[[col_stock]] > 0 & 
      inventory_data[[col_stock]] <= 10, 
    ]
    ok_stock <- inventory_data[inventory_data[[col_stock]] > 10, ]
    low_stock_count <- nrow(low_stock)
    ok_stock_count <- nrow(ok_stock)
  }
  
  out_of_stock_count <- nrow(out_of_stock)
  
  cat("  Out of Stock:  ", format_number(out_of_stock_count), 
      " (", round(out_of_stock_count / item_count * 100, 1), "%)\n", sep = "")
  cat("  Low Stock:     ", format_number(low_stock_count),
      " (", round(low_stock_count / item_count * 100, 1), "%)\n", sep = "")
  cat("  OK:            ", format_number(ok_stock_count),
      " (", round(ok_stock_count / item_count * 100, 1), "%)\n", sep = "")
  
  if (out_of_stock_count > 0 && !is.null(col_product)) {
    cat("\n  Out of Stock Items:\n")
    for (i in 1:min(10, out_of_stock_count)) {
      cat("    - ", out_of_stock[[col_product]][i], "\n")
    }
    if (out_of_stock_count > 10) {
      cat("    ... and", out_of_stock_count - 10, "more\n")
    }
  }
} else {
  cat("  No stock column available for status analysis.\n")
}

# ============================================================
# Reorder Recommendations
# ============================================================

print_header("REORDER RECOMMENDATIONS")

if (!is.null(col_stock) && !is.null(col_reorder)) {
  needs_reorder <- inventory_data[inventory_data[[col_stock]] <= inventory_data[[col_reorder]], ]
  needs_reorder <- needs_reorder[order(needs_reorder[[col_stock]]), ]
  reorder_count <- nrow(needs_reorder)
  
  cat("  Items needing reorder: ", format_number(reorder_count), "\n\n", sep = "")
  
  if (reorder_count > 0) {
    cat(sprintf("  %-30s %10s %10s %10s\n", "Product", "Stock", "Reorder", "To Order"))
    cat("  ", paste(rep("-", 64), collapse = ""), "\n", sep = "")
    
    for (i in 1:min(15, reorder_count)) {
      prod_name <- if (!is.null(col_product)) substr(needs_reorder[[col_product]][i], 1, 28) else paste("Item", i)
      reorder_qty <- needs_reorder[[col_reorder]][i] - needs_reorder[[col_stock]][i] + 10
      cat(sprintf("  %-30s %10s %10s %10s\n",
          prod_name,
          format_number(needs_reorder[[col_stock]][i]),
          format_number(needs_reorder[[col_reorder]][i]),
          format_number(max(0, reorder_qty))))
    }
    
    if (reorder_count > 15) {
      cat("  ... and", reorder_count - 15, "more items\n")
    }
  }
} else {
  cat("  No reorder point column available.\n")
  cat("  Using stock threshold of 10 units for reorder suggestions.\n\n")
  
  if (!is.null(col_stock)) {
    needs_reorder <- inventory_data[inventory_data[[col_stock]] <= 10, ]
    needs_reorder <- needs_reorder[order(needs_reorder[[col_stock]]), ]
    reorder_count <- nrow(needs_reorder)
    cat("  Items with stock <= 10: ", format_number(reorder_count), "\n\n", sep = "")
    
    if (reorder_count > 0 && !is.null(col_product)) {
      cat(sprintf("  %-30s %10s\n", "Product", "Stock"))
      cat("  ", paste(rep("-", 42), collapse = ""), "\n", sep = "")
      for (i in 1:min(15, reorder_count)) {
        cat(sprintf("  %-30s %10s\n",
            substr(needs_reorder[[col_product]][i], 1, 28),
            format_number(needs_reorder[[col_stock]][i])))
      }
    }
  }
}

# ============================================================
# Category Summary
# ============================================================

print_header("INVENTORY BY CATEGORY")

if (!is.null(col_category)) {
  cat_summary <- aggregate(
    inventory_data[[col_stock]],
    by = list(Category = inventory_data[[col_category]]),
    FUN = sum,
    na.rm = TRUE
  )
  names(cat_summary) <- c("Category", "Total_Stock")
  cat_summary <- cat_summary[order(cat_summary$Total_Stock, decreasing = TRUE), ]
  
  cat_count <- aggregate(
    rep(1, nrow(inventory_data)),
    by = list(Category = inventory_data[[col_category]]),
    FUN = sum
  )
  names(cat_count) <- c("Category", "Item_Count")
  
  cat_summary <- merge(cat_summary, cat_count, by = "Category", all = TRUE)
  cat_summary <- cat_summary[order(cat_summary$Total_Stock, decreasing = TRUE), ]
  
  cat(sprintf("  %-20s %8s %12s\n", "Category", "Items", "Stock"))
  cat("  ", paste(rep("-", 44), collapse = ""), "\n", sep = "")
  
  for (i in 1:nrow(cat_summary)) {
    cat(sprintf("  %-20s %8s %12s\n",
        substr(cat_summary$Category[i], 1, 18),
        format_number(cat_summary$Item_Count[i]),
        format_number(cat_summary$Total_Stock[i])))
  }
} else {
  cat("  No category column available.\n")
}

# ============================================================
# Supplier Summary (if available)
# ============================================================

print_header("SUPPLIER SUMMARY")

if (!is.null(col_supplier)) {
  supplier_summary <- aggregate(
    inventory_data[[col_stock]],
    by = list(Supplier = inventory_data[[col_supplier]]),
    FUN = sum,
    na.rm = TRUE
  )
  names(supplier_summary) <- c("Supplier", "Total_Stock")
  supplier_summary <- supplier_summary[order(supplier_summary$Total_Stock, decreasing = TRUE), ]
  
  cat(sprintf("  %-20s %12s\n", "Supplier", "Stock"))
  cat("  ", paste(rep("-", 35), collapse = ""), "\n", sep = "")
  
  for (i in 1:nrow(supplier_summary)) {
    cat(sprintf("  %-20s %12s\n",
        substr(supplier_summary$Supplier[i], 1, 18),
        format_number(supplier_summary$Total_Stock[i])))
  }
} else {
  cat("  No supplier column available.\n")
}

# ============================================================
# Price Analysis
# ============================================================

print_header("PRICE ANALYSIS")

if (!is.null(col_price)) {
  cat("  Min Price:    ", format_currency(min(inventory_data[[col_price]])), "\n")
  cat("  Max Price:    ", format_currency(max(inventory_data[[col_price]])), "\n")
  cat("  Mean Price:   ", format_currency(mean(inventory_data[[col_price]])), "\n")
  cat("  Median Price: ", format_currency(median(inventory_data[[col_price]])), "\n")
  
  # Price distribution
  price_ranges <- cut(inventory_data[[col_price]], 
                       breaks = c(0, 10, 50, 100, 500, Inf),
                       labels = c("$0-10", "$10-50", "$50-100", "$100-500", "$500+"))
  price_dist <- table(price_ranges)
  
  cat("\n  Price Distribution:\n")
  for (i in seq_along(price_dist)) {
    pct <- round(price_dist[i] / sum(price_dist) * 100, 1)
    cat("    ", names(price_dist)[i], ": ", price_dist[i], " (", pct, "%)\n", sep = "")
  }
} else {
  cat("  No price column available.\n")
}

# ============================================================
# Final Summary
# ============================================================

print_header("FINAL SUMMARY")

cat("  File Analyzed:         ", inventory_file, "\n")
cat("  Total Items:           ", format_number(item_count), "\n")
cat("  Total Stock Units:     ", format_number(total_stock), "\n")

if (exists("total_value")) {
  cat("  Total Inventory Value: ", format_currency(total_value), "\n")
}

if (exists("out_of_stock_count")) {
  cat("  Out of Stock Items:    ", format_number(out_of_stock_count), "\n")
  cat("  Low Stock Items:       ", format_number(low_stock_count), "\n")
  cat("  Healthy Stock Items:   ", format_number(ok_stock_count), "\n")
}

# Save output to file
if (!dir.exists(dirname(output_file))) {
  dir.create(dirname(output_file), recursive = TRUE)
}

sink(output_file)
cat("R Inventory Summary Report\n")
cat("==========================\n\n")
cat("File:", inventory_file, "\n")
cat("Total Items:", format_number(item_count), "\n")
cat("Total Stock Units:", format_number(total_stock), "\n")
if (exists("total_value")) {
  cat("Total Inventory Value:", format_currency(total_value), "\n")
}
cat("Out of Stock:", if (exists("out_of_stock_count")) format_number(out_of_stock_count) else "N/A", "\n")
cat("Low Stock:", if (exists("low_stock_count")) format_number(low_stock_count) else "N/A", "\n")
sink()

cat("\nReport saved to:", output_file, "\n")
cat("Analysis complete.\n")