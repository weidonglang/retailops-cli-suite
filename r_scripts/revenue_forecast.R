#!/usr/bin/env Rscript
#
# revenue_forecast.R
#
# Revenue Trend and Forecast Analysis Script for RetailOps CLI Suite
#
# Analyzes monthly revenue data to calculate trends, growth rates,
# moving averages, and identify best/worst performing months.
#
# Usage:
#   Rscript r_scripts/revenue_forecast.R examples/monthly_revenue.csv
#
# Outputs:
#   - Revenue trend summary
#   - Growth rates analysis
#   - Moving average trends
#   - Best and worst months
#   - Revenue distribution
#
# This script uses only base R (no external packages).

# ---- Command-Line Argument Parsing ----
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  cat("ERROR: Missing arguments.\n")
  cat("Usage: Rscript r_scripts/revenue_forecast.R <monthly_revenue_csv>\n")
  quit(status = 1)
}

revenue_file <- args[1]

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
  cat("Rows:", nrow(data), "\n\n")
  return(data)
}

# Format money as currency string
format_money <- function(value) {
  sprintf("$%.2f", value)
}

# Format percentage
format_percent <- function(value, digits = 2) {
  sprintf("%.2f%%", value * 100)
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

# Calculate simple moving average
moving_average <- function(values, window = 3) {
  n <- length(values)
  result <- rep(NA, n)
  half <- floor(window / 2)
  for (i in 1:n) {
    start_idx <- max(1, i - half)
    end_idx <- min(n, i + half)
    actual_vals <- values[start_idx:end_idx]
    actual_vals <- actual_vals[!is.na(actual_vals)]
    if (length(actual_vals) > 0) {
      result[i] <- mean(actual_vals)
    }
  }
  return(result)
}

# ---- Load Data ----
cat("============================================================\n")
cat("  R Revenue Forecast Report\n")
cat("============================================================\n\n")

raw_data <- read_csv_safe(revenue_file)

# ---- Data Validation ----
# Check for expected column patterns
has_total_revenue <- "total_revenue" %in% names(raw_data)
has_revenue <- "revenue" %in% names(raw_data)
has_month <- "month" %in% names(raw_data)
has_year <- "year" %in% names(raw_data)

if (!has_total_revenue && !has_revenue) {
  cat("ERROR: Missing revenue column. Need 'total_revenue' or 'revenue'.\n")
  quit(status = 1)
}

# ---- Data Aggregation ----
# Determine revenue column
rev_col <- ifelse(has_total_revenue, "total_revenue", "revenue")

# If data has year+month, aggregate to monthly total
if (has_year && has_month) {
  cat("Data has year and month columns - aggregating by month...\n")
  # Create month key
  raw_data$year <- as.character(raw_data$year)
  raw_data$month <- as.character(raw_data$month)
  raw_data$month_padded <- ifelse(nchar(raw_data$month) == 1,
    paste0("0", raw_data$month), raw_data$month)
  raw_data$month_key <- paste0(raw_data$year, "-", raw_data$month_padded)
  raw_data[[rev_col]] <- as.numeric(raw_data[[rev_col]])

  # Aggregate by month
  aggregated <- aggregate(
    as.formula(paste(rev_col, "~ month_key")),
    data = raw_data,
    FUN = sum,
    na.rm = TRUE
  )
  names(aggregated) <- c("month", "revenue")
  revenue_data <- aggregated[order(aggregated$month), ]
  cat(sprintf("Aggregated to %d monthly records\n\n", nrow(revenue_data)))
} else if (has_month) {
  # Already in monthly format
  revenue_data <- raw_data
  revenue_data$revenue <- as.numeric(revenue_data[[rev_col]])
  revenue_data <- revenue_data[!is.na(revenue_data$revenue), ]
  revenue_data <- revenue_data[order(revenue_data$month), ]
} else {
  # Try to use first two columns as period and revenue
  cat("Using first two columns as period and revenue...\n")
  revenue_data <- raw_data
  names(revenue_data)[1] <- "month"
  names(revenue_data)[2] <- "revenue"
  revenue_data$revenue <- as.numeric(revenue_data$revenue)
  revenue_data <- revenue_data[!is.na(revenue_data$revenue), ]
}

# Extract year from month
revenue_data$year <- substr(revenue_data$month, 1, 4)

# Sort by month
revenue_data <- revenue_data[order(revenue_data$month), ]

# Calculate derived metrics
revenue_data$prev_revenue <- c(NA, head(revenue_data$revenue, -1))
revenue_data$growth <- (revenue_data$revenue - revenue_data$prev_revenue) / revenue_data$prev_revenue
revenue_data$ma_3 <- moving_average(revenue_data$revenue, 3)
revenue_data$ma_6 <- moving_average(revenue_data$revenue, 6)

cat(sprintf("Cleaned data: %d monthly records\n\n", nrow(revenue_data)))

# ---- Basic Statistics ----
print_header("BASIC REVENUE STATISTICS")

total_revenue <- sum(revenue_data$revenue)
mean_revenue <- mean(revenue_data$revenue)
median_revenue <- median(revenue_data$revenue)
min_revenue <- min(revenue_data$revenue)
max_revenue <- max(revenue_data$revenue)
sd_revenue <- sd(revenue_data$revenue)

cat(sprintf("Total Months:           %d\n", nrow(revenue_data)))
cat(sprintf("Total Revenue:          %s\n", format_money(total_revenue)))
cat(sprintf("Average Monthly Revenue:%s\n", format_money(mean_revenue)))
cat(sprintf("Median Monthly Revenue: %s\n", format_money(median_revenue)))
cat(sprintf("Minimum Revenue:        %s\n", format_money(min_revenue)))
cat(sprintf("Maximum Revenue:        %s\n", format_money(max_revenue)))
cat(sprintf("Std Deviation:          %s\n", format_money(sd_revenue)))
cat(sprintf("Coeff of Variation:     %.2f%%\n", sd_revenue / mean_revenue * 100))

# ---- Monthly Revenue Table ----
print_header("MONTHLY REVENUE DETAILS")
cat(sprintf("%-12s %15s %15s %15s %15s\n",
  "Month", "Revenue", "Growth", "MA(3)", "MA(6)"))
print_separator()
for (i in 1:nrow(revenue_data)) {
  row <- revenue_data[i, ]
  growth_str <- ifelse(is.na(row$growth), "N/A",
    format_percent(row$growth, 1))
  ma3_str <- ifelse(is.na(row$ma_3), "N/A", format_money(row$ma_3))
  ma6_str <- ifelse(is.na(row$ma_6), "N/A", format_money(row$ma_6))
  cat(sprintf("%-12s %15s %15s %15s %15s\n",
    row$month,
    format_money(row$revenue),
    growth_str,
    ma3_str,
    ma6_str))
}

# ---- Growth Rate Analysis ----
print_header("GROWTH RATE ANALYSIS")
growth_rates <- revenue_data$growth[!is.na(revenue_data$growth)]

avg_growth <- mean(growth_rates)
max_growth <- max(growth_rates)
min_growth <- min(growth_rates)
positive_growth <- sum(growth_rates > 0)
negative_growth <- sum(growth_rates < 0)
zero_growth <- sum(growth_rates == 0)

cat(sprintf("Average Growth Rate:    %s\n", format_percent(avg_growth, 2)))
cat(sprintf("Maximum Growth Rate:    %s\n", format_percent(max_growth, 2)))
cat(sprintf("Minimum Growth Rate:    %s\n", format_percent(min_growth, 2)))
cat(sprintf("Positive Growth Months: %d (%.1f%%)\n",
  positive_growth, positive_growth / length(growth_rates) * 100))
cat(sprintf("Negative Growth Months: %d (%.1f%%)\n",
  negative_growth, negative_growth / length(growth_rates) * 100))
cat(sprintf("Zero Growth Months:     %d (%.1f%%)\n",
  zero_growth, zero_growth / length(growth_rates) * 100))

# Top growth months
print_subheader("TOP 5 GROWTH MONTHS")
growth_df <- data.frame(
  month = revenue_data$month[-1],
  growth = revenue_data$growth[-1],
  revenue = revenue_data$revenue[-1],
  stringsAsFactors = FALSE
)
growth_df <- growth_df[order(-growth_df$growth), ]
top_growth <- head(growth_df, 5)
cat(sprintf("%-12s %15s %15s\n", "Month", "Revenue", "Growth"))
print_separator()
for (i in 1:nrow(top_growth)) {
  cat(sprintf("%-12s %15s %15s\n",
    top_growth$month[i],
    format_money(top_growth$revenue[i]),
    format_percent(top_growth$growth[i], 2)))
}

# Worst growth months
print_subheader("BOTTOM 5 GROWTH MONTHS")
bottom_growth <- tail(growth_df[order(-growth_df$growth), ], 5)
cat(sprintf("%-12s %15s %15s\n", "Month", "Revenue", "Growth"))
print_separator()
for (i in 1:nrow(bottom_growth)) {
  cat(sprintf("%-12s %15s %15s\n",
    bottom_growth$month[i],
    format_money(bottom_growth$revenue[i]),
    format_percent(bottom_growth$growth[i], 2)))
}

# ---- Moving Average Analysis ----
print_header("MOVING AVERAGE ANALYSIS")
cat(sprintf("Window Size (MA-3):    3 months\n"))
cat(sprintf("Window Size (MA-6):    6 months\n\n"))

# Compare MA trends
ma3_values <- revenue_data$ma_3[!is.na(revenue_data$ma_3)]
ma6_values <- revenue_data$ma_6[!is.na(revenue_data$ma_6)]

cat(sprintf("MA-3 Average:          %s\n", format_money(mean(ma3_values))))
cat(sprintf("MA-3 Min:              %s\n", format_money(min(ma3_values))))
cat(sprintf("MA-3 Max:              %s\n", format_money(max(ma3_values))))
cat("\n")
cat(sprintf("MA-6 Average:          %s\n", format_money(mean(ma6_values))))
cat(sprintf("MA-6 Min:              %s\n", format_money(min(ma6_values))))
cat(sprintf("MA-6 Max:              %s\n", format_money(max(ma6_values))))

# MA trend direction
ma_upward <- sum(diff(ma3_values) > 0, na.rm = TRUE)
ma_downward <- sum(diff(ma3_values) < 0, na.rm = TRUE)
cat(sprintf("\nMA-3 Upward Months:   %d\n", ma_upward))
cat(sprintf("MA-3 Downward Months: %d\n", ma_downward))

# ---- Best and Worst Months ----
print_header("BEST AND WORST MONTHS")

# Best month
best_idx <- which.max(revenue_data$revenue)
best_month <- revenue_data[best_idx, ]
cat(sprintf("Best Month:\n"))
cat(sprintf("  Month:   %s\n", best_month$month))
cat(sprintf("  Revenue: %s\n", format_money(best_month$revenue)))
if (best_idx > 1) {
  cat(sprintf("  Growth:  %s\n", format_percent(best_month$growth, 2)))
}
cat("\n")

# Worst month
worst_idx <- which.min(revenue_data$revenue)
worst_month <- revenue_data[worst_idx, ]
cat(sprintf("Worst Month:\n"))
cat(sprintf("  Month:   %s\n", worst_month$month))
cat(sprintf("  Revenue: %s\n", format_money(worst_month$revenue)))
if (worst_idx > 1) {
  cat(sprintf("  Growth:  %s\n", format_percent(worst_month$growth, 2)))
}

# ---- Revenue Distribution ----
print_header("REVENUE DISTRIBUTION")
revenue <- revenue_data$revenue
breaks <- seq(floor(min_revenue / 20000) * 20000,
  ceiling(max_revenue / 20000) * 20000, by = 20000)
hist_counts <- hist(revenue, breaks = breaks, plot = FALSE)
cat(sprintf("%-25s %10s %10s\n", "Revenue Range", "Count", "Pct"))
print_separator()
for (i in 1:(length(hist_counts$breaks) - 1)) {
  low <- hist_counts$breaks[i]
  high <- hist_counts$breaks[i + 1]
  cnt <- hist_counts$counts[i]
  pct <- cnt / nrow(revenue_data)
  cat(sprintf("%-25s %10d %10s\n",
    sprintf("%s-%s", format_money(low), format_money(high)),
    cnt,
    format_percent(pct, 1)))
}

# ---- Trend Line Estimation ----
print_header("TREND ESTIMATION")
months_num <- 1:nrow(revenue_data)
trend_fit <- lm(revenue ~ months_num, data = revenue_data)
trend_coef <- coef(trend_fit)
trend_slope <- trend_coef[2]

cat(sprintf("Linear Trend Slope:    %s per month\n", format_money(trend_slope)))
cat(sprintf("Intercept:             %s\n", format_money(trend_coef[1])))
cat(sprintf("R-squared:             %.4f\n", summary(trend_fit)$r.squared))

if (trend_slope > 0) {
  cat("Trend Direction:        UPWARD (positive growth trend)\n")
} else if (trend_slope < 0) {
  cat("Trend Direction:        DOWNWARD (negative growth trend)\n")
} else {
  cat("Trend Direction:        STABLE (no significant trend)\n")
}

# ---- Forecast Next Month ----
print_header("NEXT MONTH FORECAST")
next_month_num <- nrow(revenue_data) + 1
forecast_revenue <- predict(trend_fit, newdata = data.frame(months_num = next_month_num))
cat(sprintf("Forecast Method:       Linear Trend Extrapolation\n"))
cat(sprintf("Next Period:           Month %d\n", next_month_num))
cat(sprintf("Forecast Revenue:      %s\n", format_money(forecast_revenue[1])))

# Confidence interval
forecast_ci <- tryCatch({
  predict(trend_fit,
    newdata = data.frame(months_num = next_month_num),
    interval = "confidence", level = 0.95)
}, error = function(e) {
  NULL
})
if (!is.null(forecast_ci)) {
  cat(sprintf("95%% CI Lower:          %s\n", format_money(forecast_ci[1, "lwr"])))
  cat(sprintf("95%% CI Upper:          %s\n", format_money(forecast_ci[1, "upr"])))
}

# ---- Year-over-Year Analysis (if multiple years) ----
years <- unique(revenue_data$year)
if (length(years) > 1) {
  print_header("YEAR-OVER-YEAR COMPARISON")
  cat(sprintf("%-10s %15s %15s\n", "Year", "Total Rev", "Avg/Month"))
  print_separator()
  for (yr in sort(years)) {
    yr_data <- revenue_data[revenue_data$year == yr, ]
    yr_total <- sum(yr_data$revenue)
    yr_avg <- mean(yr_data$revenue)
    cat(sprintf("%-10s %15s %15s\n",
      yr,
      format_money(yr_total),
      format_money(yr_avg)))
  }

  # Growth between years
  sorted_years <- sort(years)
  if (length(sorted_years) >= 2) {
    yr1_total <- sum(revenue_data[revenue_data$year == sorted_years[1], "revenue"])
    yr2_total <- sum(revenue_data[revenue_data$year == sorted_years[2], "revenue"])
    yr_growth <- (yr2_total - yr1_total) / yr1_total
    cat(sprintf("\nYear-over-Year Growth: %s\n", format_percent(yr_growth, 2)))
  }
}

# ---- Summary ----
print_header("FINAL SUMMARY")
cat(sprintf("  File Analyzed:              %s\n", revenue_file))
cat(sprintf("  Total Months:               %d\n", nrow(revenue_data)))
cat(sprintf("  Total Revenue:              %s\n", format_money(total_revenue)))
cat(sprintf("  Average Monthly Revenue:    %s\n", format_money(mean_revenue)))
cat(sprintf("  Median Monthly Revenue:     %s\n", format_money(median_revenue)))
cat(sprintf("  Best Month:                 %s (%s)\n",
  best_month$month, format_money(best_month$revenue)))
cat(sprintf("  Worst Month:                %s (%s)\n",
  worst_month$month, format_money(worst_month$revenue)))
cat(sprintf("  Average Growth Rate:        %s\n", format_percent(avg_growth, 2)))
cat(sprintf("  Trend Slope:                %s/month\n", format_money(trend_slope)))
cat(sprintf("  Next Month Forecast:        %s\n", format_money(forecast_revenue[1])))
cat(sprintf("  Positive Growth Months:     %d/%d\n",
  positive_growth, length(growth_rates)))
cat("\nAnalysis complete.\n")