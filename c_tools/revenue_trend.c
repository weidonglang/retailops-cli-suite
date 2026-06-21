/*
 * revenue_trend.c
 *
 * RetailOps CLI Suite - Revenue Trend Tool
 *
 * Usage: revenue_trend.exe <filename>
 *
 * Reads a monthly revenue CSV and outputs:
 *   - Total number of months
 *   - Total revenue
 *   - Average monthly revenue
 *   - Best month (highest revenue)
 *   - Worst month (lowest revenue)
 *
 * Compile:
 *   gcc c_tools/revenue_trend.c -o revenue_trend.exe
 *
 * Example:
 *   revenue_trend.exe examples/monthly_revenue.csv
 *
 * CSV Format:
 *   year,month,store_id,total_revenue,total_orders
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LENGTH 4096
#define MAX_MONTHS 500

/* Structure for a monthly record */
typedef struct {
    int year;
    int month;
    int store_id;
    double total_revenue;
    int total_orders;
} MonthlyRecord;

/* Structure for aggregated month data */
typedef struct {
    int year;
    int month;
    double total_revenue;
    int total_orders;
    int store_count;
} MonthAggregate;

/* Structure for revenue summary */
typedef struct {
    int record_count;
    int month_count;
    double total_revenue;
    double average_monthly_revenue;
    MonthAggregate best_month;
    MonthAggregate worst_month;
    char first_error[256];
    int has_error;
    MonthlyRecord records[MAX_MONTHS];
    MonthAggregate months[MAX_MONTHS];
} RevenueSummary;

/* Function prototypes */
void trim_trailing_newline(char *line);
int is_empty_or_header(const char *line);
const char* parse_field(const char *line, char *output, int max_len);
int count_csv_fields(const char *line);
int parse_revenue_csv(const char *filename, RevenueSummary *summary);
int find_or_create_month(RevenueSummary *summary, int year, int month);
void sort_months(MonthAggregate *months, int count);
int compare_months(const void *a, const void *b);
void print_revenue_summary(const RevenueSummary *summary, const char *filename);
void print_month_trend_table(const RevenueSummary *summary);

/*
 * Remove trailing newline characters.
 */
void trim_trailing_newline(char *line) {
    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[--len] = '\0';
    }
}

/*
 * Check if a line is empty or a header row.
 */
int is_empty_or_header(const char *line) {
    const char *p = line;
    while (*p) {
        if (!isspace((unsigned char)*p)) {
            if (strncmp(line, "year", 4) == 0) {
                return 1;
            }
            return 0;
        }
        p++;
    }
    return 1;
}

/*
 * Parse a single CSV field.
 */
const char* parse_field(const char *line, char *output, int max_len) {
    int i = 0;
    int in_quotes = 0;

    if (line == NULL || *line == '\0') {
        output[0] = '\0';
        return NULL;
    }

    while (*line && i < max_len - 1) {
        if (*line == '"') {
            in_quotes = !in_quotes;
            line++;
            continue;
        }
        if (*line == ',' && !in_quotes) {
            output[i] = '\0';
            return line + 1;
        }
        output[i++] = *line;
        line++;
    }
    output[i] = '\0';
    return NULL;
}

/*
 * Count CSV fields.
 */
int count_csv_fields(const char *line) {
    int count = 1;
    int in_quotes = 0;
    const char *p = line;

    if (line == NULL || *line == '\0') return 0;

    while (*p) {
        if (*p == '"') in_quotes = !in_quotes;
        else if (*p == ',' && !in_quotes) count++;
        p++;
    }
    return count;
}

/*
 * Find or create a month entry in the aggregated months array.
 * Returns the index of the month.
 */
int find_or_create_month(RevenueSummary *summary, int year, int month) {
    int i;
    for (i = 0; i < summary->month_count; i++) {
        if (summary->months[i].year == year && summary->months[i].month == month) {
            return i;
        }
    }

    /* Create new month entry */
    if (summary->month_count >= MAX_MONTHS) {
        return -1;
    }

    summary->months[summary->month_count].year = year;
    summary->months[summary->month_count].month = month;
    summary->months[summary->month_count].total_revenue = 0.0;
    summary->months[summary->month_count].total_orders = 0;
    summary->months[summary->month_count].store_count = 0;

    return summary->month_count++;
}

/*
 * Parse the monthly revenue CSV file.
 */
int parse_revenue_csv(const char *filename, RevenueSummary *summary) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int record_index = 0;

    /* Initialize summary */
    summary->record_count = 0;
    summary->month_count = 0;
    summary->total_revenue = 0.0;
    summary->average_monthly_revenue = 0.0;
    memset(&summary->best_month, 0, sizeof(summary->best_month));
    memset(&summary->worst_month, 0, sizeof(summary->worst_month));
    summary->first_error[0] = '\0';
    summary->has_error = 0;

    /* Open file */
    file = fopen(filename, "r");
    if (file == NULL) {
        snprintf(summary->first_error, sizeof(summary->first_error),
                 "Cannot open file: %s", filename);
        summary->has_error = 1;
        return 1;
    }

    /* Read and parse */
    while (fgets(line, sizeof(line), file) != NULL) {
        char field[256];
        const char *next;
        int field_index = 0;
        MonthlyRecord record;
        int fields;
        int month_idx;

        line_number++;
        trim_trailing_newline(line);

        if (is_empty_or_header(line)) {
            continue;
        }

        fields = count_csv_fields(line);
        if (fields < 5) {
            if (summary->first_error[0] == '\0') {
                snprintf(summary->first_error, sizeof(summary->first_error),
                         "Line %d: expected 5 fields, got %d",
                         line_number, fields);
            }
            continue;
        }

        memset(&record, 0, sizeof(record));

        next = line;
        while (next && *next && field_index < 5) {
            next = parse_field(next, field, sizeof(field));

            switch (field_index) {
                case 0: record.year = atoi(field); break;
                case 1: record.month = atoi(field); break;
                case 2: record.store_id = atoi(field); break;
                case 3: record.total_revenue = strtod(field, NULL); break;
                case 4: record.total_orders = atoi(field); break;
            }
            field_index++;
        }

        /* Store record */
        if (record_index < MAX_MONTHS) {
            summary->records[record_index] = record;
        }
        record_index++;
        summary->record_count++;

        /* Aggregate by month */
        month_idx = find_or_create_month(summary, record.year, record.month);
        if (month_idx >= 0) {
            summary->months[month_idx].total_revenue += record.total_revenue;
            summary->months[month_idx].total_orders += record.total_orders;
            summary->months[month_idx].store_count++;
        }

        summary->total_revenue += record.total_revenue;
    }

    if (ferror(file)) {
        snprintf(summary->first_error, sizeof(summary->first_error),
                 "Error reading file: %s", filename);
        summary->has_error = 1;
        fclose(file);
        return 1;
    }

    fclose(file);
    return 0;
}

/*
 * Compare two months for sorting (by year then month).
 */
int compare_months(const void *a, const void *b) {
    const MonthAggregate *ma = (const MonthAggregate *)a;
    const MonthAggregate *mb = (const MonthAggregate *)b;

    if (ma->year != mb->year) return ma->year - mb->year;
    return ma->month - mb->month;
}

/*
 * Sort months chronologically.
 */
void sort_months(MonthAggregate *months, int count) {
    qsort(months, count, sizeof(MonthAggregate), compare_months);
}

/*
 * Print the revenue summary report.
 */
void print_revenue_summary(const RevenueSummary *summary, const char *filename) {
    int i;
    int best_idx = 0;
    int worst_idx = 0;

    if (summary->month_count == 0) return;

    /* Find best and worst months */
    for (i = 1; i < summary->month_count; i++) {
        if (summary->months[i].total_revenue > summary->months[best_idx].total_revenue) {
            best_idx = i;
        }
        if (summary->months[i].total_revenue < summary->months[worst_idx].total_revenue) {
            worst_idx = i;
        }
    }

    printf("========================================\n");
    printf("  Revenue Trend Report\n");
    printf("========================================\n");
    printf("  File:                %s\n", filename);
    printf("----------------------------------------\n");
    printf("  Total Records:       %d\n", summary->record_count);
    printf("  Distinct Months:     %d\n", summary->month_count);
    printf("----------------------------------------\n");
    printf("  Total Revenue:       $%.2f\n", summary->total_revenue);

    if (summary->month_count > 0) {
        double avg_revenue = summary->total_revenue / summary->month_count;
        printf("  Average Monthly:     $%.2f\n", avg_revenue);
        printf("----------------------------------------\n");
        printf("  Best Month:\n");
        printf("    %04d-%02d:            $%.2f\n",
               summary->months[best_idx].year,
               summary->months[best_idx].month,
               summary->months[best_idx].total_revenue);
        printf("  Worst Month:\n");
        printf("    %04d-%02d:            $%.2f\n",
               summary->months[worst_idx].year,
               summary->months[worst_idx].month,
               summary->months[worst_idx].total_revenue);
    }
    printf("========================================\n");
}

/*
 * Print monthly trend table.
 */
void print_month_trend_table(const RevenueSummary *summary) {
    int i;
    double prev_revenue = -1.0;

    if (summary->month_count == 0) return;

    printf("\n  MONTHLY TREND:\n");
    printf("  %-10s %-12s %-12s %s\n", "Month", "Revenue", "Orders", "Change");
    printf("  %-10s %-12s %-12s %s\n",
           "----------", "------------", "------------", "----------");

    for (i = 0; i < summary->month_count; i++) {
        double change = 0.0;
        char change_str[32];

        if (prev_revenue >= 0 && prev_revenue > 0) {
            change = ((summary->months[i].total_revenue - prev_revenue) / prev_revenue) * 100.0;
            snprintf(change_str, sizeof(change_str), "%+.1f%%", change);
        } else {
            snprintf(change_str, sizeof(change_str), "-");
        }

        printf("  %04d-%02d    $%-10.2f %-12d %s\n",
               summary->months[i].year,
               summary->months[i].month,
               summary->months[i].total_revenue,
               summary->months[i].total_orders,
               change_str);

        prev_revenue = summary->months[i].total_revenue;
    }
}

/*
 * Main entry point.
 */
int main(int argc, char *argv[]) {
    RevenueSummary summary;

    printf("Revenue Trend Tool - RetailOps CLI Suite\n");
    printf("========================================\n\n");

    if (argc < 2) {
        fprintf(stderr, "ERROR: Missing filename argument.\n");
        fprintf(stderr, "Usage: %s <filename>\n", argv[0] ? argv[0] : "revenue_trend");
        fprintf(stderr, "Example: %s examples/monthly_revenue.csv\n",
                argv[0] ? argv[0] : "revenue_trend");
        return 1;
    }

    printf("Reading revenue data from: %s\n\n", argv[1]);

    if (parse_revenue_csv(argv[1], &summary) != 0) {
        fprintf(stderr, "ERROR: %s\n", summary.first_error);
        return 1;
    }

    if (summary.record_count == 0) {
        fprintf(stderr, "ERROR: No revenue records found in file.\n");
        return 1;
    }

    /* Sort months chronologically */
    sort_months(summary.months, summary.month_count);

    /* Print reports */
    print_revenue_summary(&summary, argv[1]);
    print_month_trend_table(&summary);

    printf("\nRevenue trend analysis complete.\n");
    return 0;
}