/*
 * inventory_check.c
 *
 * RetailOps CLI Suite - Inventory Check Tool
 *
 * Usage: inventory_check.exe <filename>
 *
 * Reads an inventory CSV and outputs:
 *   - Total item count
 *   - Total stock quantity
 *   - Low stock item count
 *   - Out of stock item count
 *
 * Compile:
 *   gcc c_tools/inventory_check.c -o inventory_check.exe
 *
 * Example:
 *   inventory_check.exe examples/inventory.csv
 *
 * CSV Format:
 *   product_id,product_name,category,current_stock,reorder_point,unit_cost,supplier
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

#define MAX_LINE_LENGTH 4096
#define MAX_FILENAME_LENGTH 1024
#define MAX_ITEMS 500

/* CSV field indices */
#define COL_PRODUCT_ID    0
#define COL_PRODUCT_NAME  1
#define COL_CATEGORY      2
#define COL_CURRENT_STOCK 3
#define COL_REORDER_POINT 4
#define COL_UNIT_COST     5
#define COL_SUPPLIER      6
#define EXPECTED_COLUMNS  7

/* Stock status constants */
#define STATUS_OUT_OF_STOCK 0
#define STATUS_LOW_STOCK    1
#define STATUS_OK           2

/* Structure for an inventory item */
typedef struct {
    int product_id;
    char product_name[128];
    char category[64];
    int current_stock;
    int reorder_point;
    double unit_cost;
    char supplier[64];
    int stock_status;
} InventoryItem;

/* Structure for inventory summary */
typedef struct {
    int item_count;
    int items_loaded;
    int items_skipped;
    long long total_stock;
    int low_stock_count;
    int out_of_stock_count;
    int ok_count;
    char first_error[256];
    int has_error;
    InventoryItem items[MAX_ITEMS];
} InventorySummary;

/* Function prototypes */
void trim_trailing_newline(char *line);
int is_empty_or_header(const char *line);
int parse_inventory_csv(const char *filename, InventorySummary *summary);
int assign_stock_status(int current_stock, int reorder_point);
void print_inventory_summary(const InventorySummary *summary, const char *filename);
void print_item_table(const InventorySummary *summary);
void safe_strncpy(char *dest, const char *src, size_t dest_size);
int safe_str_to_int(const char *str, int *out);
int safe_str_to_double(const char *str, double *out);

/*
 * Remove trailing newline characters from a string.
 */
void trim_trailing_newline(char *line) {
    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r')) {
        line[--len] = '\0';
    }
}

/*
 * Safe string copy that guarantees NUL termination.
 */
void safe_strncpy(char *dest, const char *src, size_t dest_size) {
    if (dest_size == 0) return;
    strncpy(dest, src, dest_size - 1);
    dest[dest_size - 1] = '\0';
}

/*
 * Safe string to int conversion using strtol.
 * Returns 0 on success, 1 on error.
 */
int safe_str_to_int(const char *str, int *out) {
    char *endptr = NULL;
    long val;

    if (str == NULL || *str == '\0') {
        return 1;
    }

    errno = 0;
    val = strtol(str, &endptr, 10);

    if (errno != 0) {
        return 1;
    }
    if (endptr == str) {
        return 1; /* No digits found */
    }
    /* Allow trailing whitespace but not other characters */
    while (*endptr) {
        if (!isspace((unsigned char)*endptr)) {
            return 1;
        }
        endptr++;
    }
    if (val < -2147483647L - 1L || val > 2147483647L) {
        return 1;
    }

    *out = (int)val;
    return 0;
}

/*
 * Safe string to double conversion using strtod.
 * Returns 0 on success, 1 on error.
 */
int safe_str_to_double(const char *str, double *out) {
    char *endptr = NULL;

    if (str == NULL || *str == '\0') {
        return 1;
    }

    errno = 0;
    *out = strtod(str, &endptr);

    if (errno != 0) {
        return 1;
    }
    if (endptr == str) {
        return 1; /* No digits found */
    }
    /* Allow trailing whitespace but not other characters */
    while (*endptr) {
        if (!isspace((unsigned char)*endptr)) {
            return 1;
        }
        endptr++;
    }

    return 0;
}

/*
 * Check if a line is empty or a header row.
 * Returns 1 if should be skipped, 0 otherwise.
 */
int is_empty_or_header(const char *line) {
    const char *p = line;
    while (*p) {
        if (!isspace((unsigned char)*p)) {
            /* Check if first word is 'product_id' (header) */
            if (strncmp(line, "product_id", 10) == 0) {
                return 1;
            }
            return 0;
        }
        p++;
    }
    return 1; /* Empty line */
}

/*
 * Parse a single CSV field.
 * Skips past comma and quote boundaries.
 * Returns pointer to next field position, or NULL if at end.
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
            return line + 1; /* Skip past comma */
        }
        output[i++] = *line;
        line++;
    }
    output[i] = '\0';
    return NULL; /* End of string */
}

/*
 * Count fields in a CSV line.
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
 * Determine stock status based on current stock and reorder point.
 */
int assign_stock_status(int current_stock, int reorder_point) {
    if (current_stock <= 0) {
        return STATUS_OUT_OF_STOCK;
    } else if (current_stock <= reorder_point) {
        return STATUS_LOW_STOCK;
    } else {
        return STATUS_OK;
    }
}

/*
 * Parse the inventory CSV file and populate the summary.
 * Returns 0 on success, 1 on error.
 */
int parse_inventory_csv(const char *filename, InventorySummary *summary) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int item_index = 0;
    int skipped = 0;

    /* Initialize summary */
    summary->item_count = 0;
    summary->items_loaded = 0;
    summary->items_skipped = 0;
    summary->total_stock = 0;
    summary->low_stock_count = 0;
    summary->out_of_stock_count = 0;
    summary->ok_count = 0;
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

    /* Read and parse each line */
    while (fgets(line, sizeof(line), file) != NULL) {
        char field[256];
        const char *next;
        int field_index = 0;
        InventoryItem item;
        int fields;

        line_number++;
        trim_trailing_newline(line);

        /* Skip empty lines and header */
        if (is_empty_or_header(line)) {
            continue;
        }

        /* Check field count */
        fields = count_csv_fields(line);
        if (fields < EXPECTED_COLUMNS) {
            if (summary->first_error[0] == '\0') {
                snprintf(summary->first_error, sizeof(summary->first_error),
                         "Line %d: expected %d fields, got %d",
                         line_number, EXPECTED_COLUMNS, fields);
            }
            continue;
        }

        /* Reset item */
        memset(&item, 0, sizeof(item));

        /* Parse fields */
        next = line;
        while (next && *next && field_index < EXPECTED_COLUMNS) {
            next = parse_field(next, field, sizeof(field));

            switch (field_index) {
                case COL_PRODUCT_ID:
                    safe_str_to_int(field, &item.product_id);
                    break;
                case COL_PRODUCT_NAME:
                    safe_strncpy(item.product_name, field, sizeof(item.product_name));
                    break;
                case COL_CATEGORY:
                    safe_strncpy(item.category, field, sizeof(item.category));
                    break;
                case COL_CURRENT_STOCK:
                    safe_str_to_int(field, &item.current_stock);
                    break;
                case COL_REORDER_POINT:
                    safe_str_to_int(field, &item.reorder_point);
                    break;
                case COL_UNIT_COST:
                    safe_str_to_double(field, &item.unit_cost);
                    break;
                case COL_SUPPLIER:
                    safe_strncpy(item.supplier, field, sizeof(item.supplier));
                    break;
            }
            field_index++;
        }

        /* Assign stock status */
        item.stock_status = assign_stock_status(item.current_stock, item.reorder_point);

        summary->item_count++;

        /* Bounds check: skip storing in array if capacity exceeded */
        if (item_index >= MAX_ITEMS) {
            skipped++;
            continue;
        }

        /* Store item */
        summary->items[item_index] = item;
        item_index++;

        /* Update summary stats (only for items we've stored) */
        summary->total_stock += item.current_stock;

        switch (item.stock_status) {
            case STATUS_OUT_OF_STOCK:
                summary->out_of_stock_count++;
                break;
            case STATUS_LOW_STOCK:
                summary->low_stock_count++;
                break;
            case STATUS_OK:
                summary->ok_count++;
                break;
        }
    }

    fclose(file);
    summary->items_loaded = item_index;
    summary->items_skipped = skipped;
    return 0;
}

/*
 * Print inventory summary report.
 */
void print_inventory_summary(const InventorySummary *summary, const char *filename) {
    printf("========================================\n");
    printf("  Inventory Check Report\n");
    printf("========================================\n");
    printf("  File:                %s\n", filename);
    printf("----------------------------------------\n");
    printf("  Total Items Read:    %d\n", summary->item_count);
    printf("  Items Loaded:        %d\n", summary->items_loaded);
    if (summary->items_skipped > 0) {
        printf("  Items Skipped:       %d (capacity exceeded)\n", summary->items_skipped);
    }
    printf("----------------------------------------\n");
    printf("  Total Stock:         %I64d\n", summary->total_stock);
    printf("  Out of Stock:        %d\n", summary->out_of_stock_count);
    printf("  Low Stock:           %d\n", summary->low_stock_count);
    printf("  OK:                  %d\n", summary->ok_count);
    printf("----------------------------------------\n");

    if (summary->items_loaded > 0) {
        double out_pct = (double)summary->out_of_stock_count / summary->items_loaded * 100.0;
        double low_pct = (double)summary->low_stock_count / summary->items_loaded * 100.0;
        double ok_pct = (double)summary->ok_count / summary->items_loaded * 100.0;
        printf("  Out of Stock Rate:   %.1f%%\n", out_pct);
        printf("  Low Stock Rate:      %.1f%%\n", low_pct);
        printf("  OK Rate:             %.1f%%\n", ok_pct);
    }
    printf("========================================\n");
}

/*
 * Print item details (low stock and out of stock).
 */
void print_item_table(const InventorySummary *summary) {
    int i;
    int problem_count = 0;

    if (summary->items_loaded == 0) return;

    printf("\n  ITEMS REQUIRING ATTENTION:\n");
    printf("  %-8s %-20s %-12s %-12s %s\n",
           "ID", "Product", "Stock", "Reorder", "Status");
    printf("  %-8s %-20s %-12s %-12s %s\n",
           "--------", "--------------------", "------------",
           "------------", "-------------");

    for (i = 0; i < summary->items_loaded && i < MAX_ITEMS; i++) {
        if (summary->items[i].stock_status == STATUS_OK) continue;

        const char *status;
        if (summary->items[i].stock_status == STATUS_OUT_OF_STOCK) {
            status = "OUT OF STOCK";
        } else {
            status = "LOW STOCK";
        }

        printf("  %-8d %-20s %-12d %-12d %s\n",
               summary->items[i].product_id,
               summary->items[i].product_name,
               summary->items[i].current_stock,
               summary->items[i].reorder_point,
               status);
        problem_count++;
    }

    if (problem_count == 0) {
        printf("  No items requiring attention.\n");
    } else {
        printf("\n  Total items needing attention: %d\n", problem_count);
    }
}

/*
 * Main entry point.
 */
int main(int argc, char *argv[]) {
    InventorySummary summary;
    char filename[MAX_FILENAME_LENGTH];

    printf("Inventory Check Tool - RetailOps CLI Suite\n");
    printf("===========================================\n\n");

    if (argc < 2) {
        fprintf(stderr, "ERROR: Missing filename argument.\n");
        fprintf(stderr, "Usage: %s <filename>\n", argv[0] ? argv[0] : "inventory_check");
        fprintf(stderr, "Example: %s examples/inventory.csv\n",
                argv[0] ? argv[0] : "inventory_check");
        return 1;
    }

    if (strlen(argv[1]) >= MAX_FILENAME_LENGTH) {
        fprintf(stderr, "ERROR: Filename too long.\n");
        return 1;
    }
    safe_strncpy(filename, argv[1], sizeof(filename));

    printf("Reading inventory from: %s\n\n", filename);

    /* Parse CSV */
    if (parse_inventory_csv(filename, &summary) != 0) {
        fprintf(stderr, "ERROR: %s\n", summary.first_error);
        return 1;
    }

    if (summary.item_count == 0) {
        fprintf(stderr, "ERROR: No inventory items found in file.\n");
        return 1;
    }

    /* Print reports */
    print_inventory_summary(&summary, filename);
    print_item_table(&summary);

    printf("\nInventory check complete.\n");
    return 0;
}