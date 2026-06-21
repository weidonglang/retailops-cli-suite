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
 * Parse the inventory CSV file and populate the summary.
 * Returns 0 on success, 1 on error.
 */
int parse_inventory_csv(const char *filename, InventorySummary *summary) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int item_index = 0;

    /* Initialize summary */
    summary->item_count = 0;
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
                    item.product_id = atoi(field);
                    break;
                case COL_PRODUCT_NAME:
                    strncpy(item.product_name, field, sizeof(item.product_name) - 1);
                    break;
                case COL_CATEGORY:
                    strncpy(item.category, field, sizeof(item.category) - 1);
                    break;
                case COL_CURRENT_STOCK:
                    item.current_stock = atoi(field);
                    break;
                case COL_REORDER_POINT:
                    item.reorder_point = atoi(field);
                    break;
                case COL_UNIT_COST:
                    item.unit_cost = strtod(field, NULL);
                    break;
                case COL_SUPPLIER:
                    strncpy(item.supplier, field, sizeof(item.supplier) - 1);
                    break;
            }
            field_index++;
        }

        /* Assign stock status */
        item.stock_status = assign_stock_status(item.current_stock, item.reorder_point);

        /* Update summary */
        if (item_index < MAX_ITEMS) {
            summary->items[item_index] = item;
            item_index++;
        }
        summary->item_count++;
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
 * Assign stock status based on current stock and reorder point.
 * Returns STATUS_OUT_OF_STOCK, STATUS_LOW_STOCK, or STATUS_OK.
 */
int assign_stock_status(int current_stock, int reorder_point) {
    if (current_stock <= 0) {
        return STATUS_OUT_OF_STOCK;
    }
    if (current_stock <= reorder_point) {
        return STATUS_LOW_STOCK;
    }
    return STATUS_OK;
}

/*
 * Print the inventory summary report.
 */
void print_inventory_summary(const InventorySummary *summary, const char *filename) {
    double total_value = 0.0;
    int i;

    /* Calculate total inventory value */
    for (i = 0; i < summary->item_count && i < MAX_ITEMS; i++) {
        total_value += summary->items[i].current_stock * summary->items[i].unit_cost;
    }

    printf("========================================\n");
    printf("  Inventory Check Report\n");
    printf("========================================\n");
    printf("  File:                %s\n", filename);
    printf("----------------------------------------\n");
    printf("  Total Items:         %d\n", summary->item_count);
    printf("  Total Stock:         %lld\n", summary->total_stock);
    printf("  Total Value:         $%.2f\n", total_value);
    printf("----------------------------------------\n");
    printf("  Stock Status:\n");
    printf("    OK Items:          %d\n", summary->ok_count);
    printf("    Low Stock Items:   %d\n", summary->low_stock_count);
    printf("    Out of Stock:      %d\n", summary->out_of_stock_count);
    printf("----------------------------------------\n");

    if (summary->item_count > 0) {
        double low_pct = (double)summary->low_stock_count / summary->item_count * 100.0;
        double oos_pct = (double)summary->out_of_stock_count / summary->item_count * 100.0;
        printf("    Low Stock Rate:    %.1f%%\n", low_pct);
        printf("    Out-of-Stock Rate: %.1f%%\n", oos_pct);
    }

    printf("========================================\n");
}

/*
 * Print low stock and out of stock items in a table.
 */
void print_item_table(const InventorySummary *summary) {
    int i;
    int printed = 0;

    /* Print out of stock items */
    printf("\n  OUT OF STOCK ITEMS:\n");
    printf("  %-6s %-25s %-12s %s\n", "ID", "Product", "Category", "Supplier");
    printf("  %-6s %-25s %-12s %s\n", "------", "-------------------------", "------------", "----------");
    for (i = 0; i < summary->item_count && i < MAX_ITEMS; i++) {
        if (summary->items[i].stock_status == STATUS_OUT_OF_STOCK) {
            printf("  %-6d %-25s %-12s %s\n",
                   summary->items[i].product_id,
                   summary->items[i].product_name,
                   summary->items[i].category,
                   summary->items[i].supplier);
            printed++;
        }
    }
    if (printed == 0) {
        printf("  (none)\n");
    }

    /* Print low stock items */
    printed = 0;
    printf("\n  LOW STOCK ITEMS (Stock <= Reorder Point):\n");
    printf("  %-6s %-25s %-8s %-8s %-10s %s\n",
           "ID", "Product", "Stock", "Reorder", "Cost", "Supplier");
    printf("  %-6s %-25s %-8s %-8s %-10s %s\n",
           "------", "-------------------------", "-------", "-------", "----------", "----------");
    for (i = 0; i < summary->item_count && i < MAX_ITEMS; i++) {
        if (summary->items[i].stock_status == STATUS_LOW_STOCK) {
            printf("  %-6d %-25s %-8d %-8d $%-8.2f %s\n",
                   summary->items[i].product_id,
                   summary->items[i].product_name,
                   summary->items[i].current_stock,
                   summary->items[i].reorder_point,
                   summary->items[i].unit_cost,
                   summary->items[i].supplier);
            printed++;
        }
    }
    if (printed == 0) {
        printf("  (none)\n");
    }
}

/*
 * Main entry point.
 */
int main(int argc, char *argv[]) {
    InventorySummary summary;

    printf("Inventory Check Tool - RetailOps CLI Suite\n");
    printf("==========================================\n\n");

    /* Check arguments */
    if (argc < 2) {
        fprintf(stderr, "ERROR: Missing filename argument.\n");
        fprintf(stderr, "Usage: %s <filename>\n", argv[0] ? argv[0] : "inventory_check");
        fprintf(stderr, "Example: %s examples/inventory.csv\n",
                argv[0] ? argv[0] : "inventory_check");
        return 1;
    }

    printf("Reading inventory from: %s\n\n", argv[1]);

    /* Parse the CSV file */
    if (parse_inventory_csv(argv[1], &summary) != 0) {
        fprintf(stderr, "ERROR: %s\n", summary.first_error);
        return 1;
    }

    /* Check if any items were found */
    if (summary.item_count == 0) {
        fprintf(stderr, "ERROR: No inventory items found in file.\n");
        return 1;
    }

    /* Print reports */
    print_inventory_summary(&summary, argv[1]);
    print_item_table(&summary);

    /* Warning if there are issues */
    if (summary.low_stock_count > 0 || summary.out_of_stock_count > 0) {
        printf("\n  WARNING: %d item(s) need attention (low or out of stock).\n",
               summary.low_stock_count + summary.out_of_stock_count);
    }

    printf("\nInventory check complete.\n");
    return 0;
}