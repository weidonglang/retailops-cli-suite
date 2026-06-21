/*
 * customer_score.c
 *
 * RetailOps CLI Suite - Customer Score Tool
 *
 * Usage: customer_score.exe <customers.csv> <orders.csv>
 *
 * Computes customer scores:
 *   score = order_count * 10 + total_revenue / 10
 *
 * Outputs Top 5 customers by score.
 *
 * Compile:
 *   gcc c_tools/customer_score.c -o customer_score.exe
 *
 * Example:
 *   customer_score.exe examples/customers.csv examples/orders.csv
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <errno.h>

#define MAX_LINE_LENGTH 4096
#define MAX_CUSTOMERS 500
#define MAX_ORDERS 2000

/* Structure for a customer record */
typedef struct {
    int customer_id;
    char name[128];
    char email[128];
    char city[64];
    char signup_date[16];
    int valid;
} CustomerRecord;

/* Structure for an order record */
typedef struct {
    int order_id;
    int customer_id;
    int store_id;
    int product_id;
    int quantity;
    double unit_price;
    double total_price;
    char order_date[16];
    int valid;
} OrderRecord;

/* Structure for customer analytics */
typedef struct {
    int customer_id;
    char name[128];
    char email[128];
    char city[64];
    int order_count;
    double total_revenue;
    double score;
} CustomerAnalytics;

/* Structure for overall summary */
typedef struct {
    int customer_count;
    int order_count;
    int customers_loaded;
    int orders_loaded;
    int customers_skipped;
    int orders_skipped;
    int lines_skipped_bad;
    CustomerAnalytics analytics[MAX_CUSTOMERS];
    int analytics_count;
    char first_error[256];
    int has_error;
} ScoreSummary;

/* Function prototypes */
void trim_trailing_newline(char *line);
int is_empty_or_header(const char *line, const char *header_prefix);
const char* parse_field(const char *line, char *output, int max_len);
int count_csv_fields(const char *line);
int parse_customers_csv(const char *filename, CustomerRecord *customers, ScoreSummary *summary);
int parse_orders_csv(const char *filename, OrderRecord *orders, ScoreSummary *summary);
int find_analytics_index(ScoreSummary *summary, int customer_id);
void build_customer_analytics(CustomerRecord *customers, int customer_count,
                               OrderRecord *orders, int order_count,
                               ScoreSummary *summary);
int compare_by_score(const void *a, const void *b);
int compare_by_id(const void *a, const void *b);
void print_top_customers(const ScoreSummary *summary, int limit);
void print_segment_summary(const ScoreSummary *summary);
double compute_score(int order_count, double total_revenue);
int safe_str_to_int(const char *str, int *out);
int safe_str_to_double(const char *str, double *out);
void safe_strncpy(char *dest, const char *src, size_t dest_size);

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

    /* Check for conversion errors */
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
    /* Check range */
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

    /* Check for conversion errors */
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
 */
int is_empty_or_header(const char *line, const char *header_prefix) {
    const char *p = line;
    while (*p) {
        if (!isspace((unsigned char)*p)) {
            if (strncmp(line, header_prefix, strlen(header_prefix)) == 0) {
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
 * Parse customers CSV file.
 * Returns 0 on success, 1 on error.
 */
int parse_customers_csv(const char *filename, CustomerRecord *customers, ScoreSummary *summary) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int customer_count = 0;
    int skipped = 0;

    file = fopen(filename, "r");
    if (file == NULL) {
        summary->has_error = 1;
        snprintf(summary->first_error, sizeof(summary->first_error),
                 "Cannot open customers file: %s", filename);
        return 1;
    }

    while (fgets(line, sizeof(line), file) != NULL) {
        char field[256];
        const char *next;
        int field_index = 0;
        int fields;
        CustomerRecord record;

        line_number++;
        trim_trailing_newline(line);

        if (is_empty_or_header(line, "customer_id")) {
            continue;
        }

        fields = count_csv_fields(line);
        if (fields < 5) {
            skipped++;
            continue;
        }

        memset(&record, 0, sizeof(record));
        record.valid = 0;

        next = line;
        while (next && *next && field_index < 5) {
            next = parse_field(next, field, sizeof(field));

            switch (field_index) {
                case 0:
                    if (safe_str_to_int(field, &record.customer_id) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 1:
                    safe_strncpy(record.name, field, sizeof(record.name));
                    break;
                case 2:
                    safe_strncpy(record.email, field, sizeof(record.email));
                    break;
                case 3:
                    safe_strncpy(record.city, field, sizeof(record.city));
                    break;
                case 4:
                    safe_strncpy(record.signup_date, field, sizeof(record.signup_date));
                    break;
            }
            field_index++;
        }

        /* Bounds check: do not exceed array capacity */
        if (customer_count >= MAX_CUSTOMERS) {
            skipped++;
            continue;
        }

        if (record.valid == 0 && record.customer_id > 0) {
            record.valid = 1;
        }

        customers[customer_count] = record;
        customers[customer_count].valid = 1;
        customer_count++;
    }

    fclose(file);
    summary->customers_loaded = customer_count;
    summary->customers_skipped = skipped;
    summary->customer_count = customer_count;
    return 0;
}

/*
 * Parse orders CSV file.
 * Returns 0 on success, 1 on error.
 */
int parse_orders_csv(const char *filename, OrderRecord *orders, ScoreSummary *summary) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int order_count = 0;
    int skipped = 0;

    file = fopen(filename, "r");
    if (file == NULL) {
        summary->has_error = 1;
        snprintf(summary->first_error, sizeof(summary->first_error),
                 "Cannot open orders file: %s", filename);
        return 1;
    }

    while (fgets(line, sizeof(line), file) != NULL) {
        char field[256];
        const char *next;
        int field_index = 0;
        int fields;
        OrderRecord record;

        line_number++;
        trim_trailing_newline(line);

        if (is_empty_or_header(line, "order_id")) {
            continue;
        }

        fields = count_csv_fields(line);
        if (fields < 7) {
            skipped++;
            continue;
        }

        memset(&record, 0, sizeof(record));
        record.valid = 0;

        next = line;
        while (next && *next && field_index < 7) {
            next = parse_field(next, field, sizeof(field));

            switch (field_index) {
                case 0:
                    if (safe_str_to_int(field, &record.order_id) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 1:
                    if (safe_str_to_int(field, &record.customer_id) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 2:
                    if (safe_str_to_int(field, &record.store_id) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 3:
                    if (safe_str_to_int(field, &record.product_id) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 4:
                    if (safe_str_to_int(field, &record.quantity) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 5:
                    if (safe_str_to_double(field, &record.unit_price) != 0) {
                        record.valid = 0;
                    }
                    break;
                case 6:
                    safe_strncpy(record.order_date, field, sizeof(record.order_date));
                    break;
            }
            field_index++;
        }

        /* Bounds check: do not exceed array capacity */
        if (order_count >= MAX_ORDERS) {
            skipped++;
            continue;
        }

        if (record.valid) {
            record.total_price = record.quantity * record.unit_price;
        }

        orders[order_count] = record;
        orders[order_count].valid = record.valid;
        order_count++;
    }

    fclose(file);
    summary->orders_loaded = order_count;
    summary->orders_skipped = skipped;
    summary->order_count = order_count;
    return 0;
}

/*
 * Compute customer score.
 * score = order_count * 10 + total_revenue / 10
 */
double compute_score(int order_count, double total_revenue) {
    return (double)order_count * 10.0 + total_revenue / 10.0;
}

/*
 * Find or create analytics entry for a customer.
 */
int find_analytics_index(ScoreSummary *summary, int customer_id) {
    int i;
    for (i = 0; i < summary->analytics_count; i++) {
        if (summary->analytics[i].customer_id == customer_id) {
            return i;
        }
    }
    return -1;
}

/*
 * Build customer analytics from customers and orders.
 */
void build_customer_analytics(CustomerRecord *customers, int customer_count,
                               OrderRecord *orders, int order_count,
                               ScoreSummary *summary) {
    int i, j;
    int *order_counts;
    double *revenues;
    int *customer_active;
    int customers_processed = 0;

    /* Initialize summary */
    summary->customer_count = customer_count;
    summary->order_count = order_count;
    summary->analytics_count = 0;
    summary->first_error[0] = '\0';
    summary->has_error = 0;

    if (customer_count <= 0) {
        return;
    }

    /* Allocate temporary arrays */
    order_counts = (int *)calloc(customer_count, sizeof(int));
    revenues = (double *)calloc(customer_count, sizeof(double));
    customer_active = (int *)calloc(customer_count, sizeof(int));

    if (!order_counts || !revenues || !customer_active) {
        summary->has_error = 1;
        snprintf(summary->first_error, sizeof(summary->first_error),
                 "Memory allocation failed");
        free(order_counts);
        free(revenues);
        free(customer_active);
        return;
    }

    /* Aggregate orders per customer */
    for (i = 0; i < order_count; i++) {
        if (!orders[i].valid) continue;

        int cust_id = orders[i].customer_id;
        int found = 0;
        /* Only search within valid customer range */
        for (j = 0; j < customer_count; j++) {
            if (customers[j].valid && customers[j].customer_id == cust_id) {
                order_counts[j]++;
                revenues[j] += orders[i].total_price;
                customer_active[j] = 1;
                found = 1;
                break;
            }
        }
        /* If customer not found, still count as unknown */
        if (!found) {
            /* Count orphan orders in a separate stat */
        }
    }

    /* Build analytics */
    for (i = 0; i < customer_count; i++) {
        if (!customers[i].valid) continue;

        /* Bounds check: ensure we don't exceed analytics array */
        if (summary->analytics_count >= MAX_CUSTOMERS) {
            break;
        }

        int idx = summary->analytics_count;
        CustomerAnalytics *ca = &summary->analytics[idx];

        ca->customer_id = customers[i].customer_id;
        safe_strncpy(ca->name, customers[i].name, sizeof(ca->name));
        safe_strncpy(ca->email, customers[i].email, sizeof(ca->email));
        safe_strncpy(ca->city, customers[i].city, sizeof(ca->city));
        ca->order_count = order_counts[i];
        ca->total_revenue = revenues[i];
        ca->score = compute_score(ca->order_count, ca->total_revenue);

        summary->analytics_count++;
        customers_processed++;
    }

    summary->lines_skipped_bad = (customer_count - customers_processed);
    if (summary->lines_skipped_bad < 0) summary->lines_skipped_bad = 0;

    free(order_counts);
    free(revenues);
    free(customer_active);
}

/*
 * Compare two analytics entries by score (descending).
 */
int compare_by_score(const void *a, const void *b) {
    const CustomerAnalytics *ca = (const CustomerAnalytics *)a;
    const CustomerAnalytics *cb = (const CustomerAnalytics *)b;

    if (cb->score > ca->score) return 1;
    if (cb->score < ca->score) return -1;
    return 0;
}

/*
 * Compare two analytics entries by ID (ascending).
 */
int compare_by_id(const void *a, const void *b) {
    const CustomerAnalytics *ca = (const CustomerAnalytics *)a;
    const CustomerAnalytics *cb = (const CustomerAnalytics *)b;

    return ca->customer_id - cb->customer_id;
}

/*
 * Print top N customers by score.
 */
void print_top_customers(const ScoreSummary *summary, int limit) {
    int i;

    if (summary->analytics_count == 0) return;

    printf("  %-5s %-22s %-12s %-12s %-12s %-12s\n",
           "Rank", "Name", "Orders", "Revenue", "Score", "Segment");
    printf("  %-5s %-22s %-12s %-12s %-12s %-12s\n",
           "-----", "----------------------", "------------", "------------",
           "------------", "------------");

    for (i = 0; i < summary->analytics_count && i < limit; i++) {
        double rev = summary->analytics[i].total_revenue;
        int ord = summary->analytics[i].order_count;
        const char *segment;

        if (rev >= 1000 || ord >= 10) segment = "VIP";
        else if (rev >= 500 || ord >= 5) segment = "LOYAL";
        else if (rev > 0) segment = "ACTIVE";
        else segment = "NEW";

        printf("  #%-3d  %-22s %-12d $%-10.2f %-11.1f %-12s\n",
               i + 1,
               summary->analytics[i].name,
               summary->analytics[i].order_count,
               summary->analytics[i].total_revenue,
               summary->analytics[i].score,
               segment);
    }
}

/*
 * Print segment summary.
 */
void print_segment_summary(const ScoreSummary *summary) {
    int i;
    int vip_count = 0, loyal_count = 0, active_count = 0, new_count = 0;

    for (i = 0; i < summary->analytics_count; i++) {
        double rev = summary->analytics[i].total_revenue;
        int ord = summary->analytics[i].order_count;

        if (rev >= 1000 || ord >= 10) vip_count++;
        else if (rev >= 500 || ord >= 5) loyal_count++;
        else if (rev > 0) active_count++;
        else new_count++;
    }

    printf("\n  SEGMENT DISTRIBUTION:\n");
    printf("  %-15s %5s\n", "Segment", "Count");
    printf("  %-15s %5s\n", "---------------", "-----");
    printf("  %-15s %5d\n", "VIP", vip_count);
    printf("  %-15s %5d\n", "LOYAL", loyal_count);
    printf("  %-15s %5d\n", "ACTIVE", active_count);
    printf("  %-15s %5d\n", "NEW", new_count);
}

/*
 * Main entry point.
 */
int main(int argc, char *argv[]) {
    CustomerRecord customers[MAX_CUSTOMERS];
    OrderRecord orders[MAX_ORDERS];
    ScoreSummary summary;

    printf("Customer Score Tool - RetailOps CLI Suite\n");
    printf("==========================================\n\n");

    if (argc < 3) {
        fprintf(stderr, "ERROR: Missing arguments.\n");
        fprintf(stderr, "Usage: %s <customers.csv> <orders.csv>\n",
                argv[0] ? argv[0] : "customer_score");
        fprintf(stderr, "Example: %s examples/customers.csv examples/orders.csv\n",
                argv[0] ? argv[0] : "customer_score");
        return 1;
    }

    printf("Reading customers from: %s\n", argv[1]);
    printf("Reading orders from: %s\n\n", argv[2]);

    /* Initialize summary */
    memset(&summary, 0, sizeof(summary));

    /* Parse customers */
    if (parse_customers_csv(argv[1], customers, &summary) != 0) {
        fprintf(stderr, "ERROR: Cannot open customers file: %s\n", argv[1]);
        return 1;
    }

    if (summary.customers_loaded == 0) {
        fprintf(stderr, "ERROR: No customer records found in file: %s\n", argv[1]);
        return 1;
    }

    printf("  Customers loaded:  %d\n", summary.customers_loaded);
    if (summary.customers_skipped > 0) {
        printf("  Customers skipped: %d (capacity exceeded)\n", summary.customers_skipped);
    }

    /* Parse orders */
    if (parse_orders_csv(argv[2], orders, &summary) != 0) {
        fprintf(stderr, "ERROR: Cannot open orders file: %s\n", argv[2]);
        return 1;
    }

    if (summary.orders_loaded == 0) {
        fprintf(stderr, "ERROR: No order records found in file: %s\n", argv[2]);
        return 1;
    }

    printf("  Orders loaded:     %d\n", summary.orders_loaded);
    if (summary.orders_skipped > 0) {
        printf("  Orders skipped:    %d (capacity exceeded)\n", summary.orders_skipped);
    }
    printf("\n");

    /* Build analytics */
    build_customer_analytics(customers, summary.customers_loaded,
                              orders, summary.orders_loaded, &summary);

    if (summary.has_error) {
        fprintf(stderr, "ERROR: %s\n", summary.first_error);
        return 1;
    }

    printf("==========================================\n");
    printf("  Customer Score Report\n");
    printf("==========================================\n");
    printf("  Customers Found:    %d\n", summary.customers_loaded);
    printf("  Orders Found:       %d\n", summary.orders_loaded);
    printf("  Customers w/Orders: %d\n\n", summary.analytics_count);

    /* Sort by score descending */
    qsort(summary.analytics, summary.analytics_count,
          sizeof(CustomerAnalytics), compare_by_score);

    /* Print top 5 */
    printf("  TOP 5 CUSTOMERS BY SCORE:\n");
    print_top_customers(&summary, 5);

    /* Print segment summary */
    print_segment_summary(&summary);

    printf("\n==========================================\n");
    printf("  Scoring Formula: score = orders * 10 + revenue / 10\n");
    printf("==========================================\n");

    printf("\nCustomer scoring complete.\n");
    return 0;
}