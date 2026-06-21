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
int parse_customers_csv(const char *filename, CustomerRecord *customers, int *count);
int parse_orders_csv(const char *filename, OrderRecord *orders, int *count);
int find_analytics_index(ScoreSummary *summary, int customer_id);
void build_customer_analytics(CustomerRecord *customers, int customer_count,
                               OrderRecord *orders, int order_count,
                               ScoreSummary *summary);
int compare_by_score(const void *a, const void *b);
int compare_by_id(const void *a, const void *b);
void print_top_customers(const ScoreSummary *summary, int limit);
void print_segment_summary(const ScoreSummary *summary);
double compute_score(int order_count, double total_revenue);

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
 */
int parse_customers_csv(const char *filename, CustomerRecord *customers, int *count) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int customer_count = 0;

    file = fopen(filename, "r");
    if (file == NULL) {
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
            continue;
        }

        memset(&record, 0, sizeof(record));
        record.valid = 0;

        next = line;
        while (next && *next && field_index < 5) {
            next = parse_field(next, field, sizeof(field));

            switch (field_index) {
                case 0: record.customer_id = atoi(field); break;
                case 1: strncpy(record.name, field, sizeof(record.name) - 1); break;
                case 2: strncpy(record.email, field, sizeof(record.email) - 1); break;
                case 3: strncpy(record.city, field, sizeof(record.city) - 1); break;
                case 4: strncpy(record.signup_date, field, sizeof(record.signup_date) - 1); break;
            }
            field_index++;
        }

        if (customer_count < MAX_CUSTOMERS) {
            customers[customer_count] = record;
            customers[customer_count].valid = 1;
            customer_count++;
        }
    }

    fclose(file);
    *count = customer_count;
    return 0;
}

/*
 * Parse orders CSV file.
 */
int parse_orders_csv(const char *filename, OrderRecord *orders, int *count) {
    FILE *file;
    char line[MAX_LINE_LENGTH];
    int line_number = 0;
    int order_count = 0;

    file = fopen(filename, "r");
    if (file == NULL) {
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
            continue;
        }

        memset(&record, 0, sizeof(record));
        record.valid = 0;

        next = line;
        while (next && *next && field_index < 7) {
            next = parse_field(next, field, sizeof(field));

            switch (field_index) {
                case 0: record.order_id = atoi(field); break;
                case 1: record.customer_id = atoi(field); break;
                case 2: record.store_id = atoi(field); break;
                case 3: record.product_id = atoi(field); break;
                case 4: record.quantity = atoi(field); break;
                case 5: record.unit_price = strtod(field, NULL); break;
                case 6: strncpy(record.order_date, field, sizeof(record.order_date) - 1); break;
            }
            field_index++;
        }

        record.total_price = record.quantity * record.unit_price;

        if (order_count < MAX_ORDERS) {
            orders[order_count] = record;
            orders[order_count].valid = 1;
            order_count++;
        }
    }

    fclose(file);
    *count = order_count;
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

    /* Initialize summary */
    summary->customer_count = customer_count;
    summary->order_count = order_count;
    summary->analytics_count = 0;
    summary->first_error[0] = '\0';
    summary->has_error = 0;

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
        for (j = 0; j < customer_count; j++) {
            if (customers[j].valid && customers[j].customer_id == cust_id) {
                order_counts[j]++;
                revenues[j] += orders[i].total_price;
                customer_active[j] = 1;
                break;
            }
        }
    }

    /* Build analytics */
    for (i = 0; i < customer_count; i++) {
        if (!customers[i].valid) continue;

        int idx = summary->analytics_count;
        CustomerAnalytics *ca = &summary->analytics[idx];

        ca->customer_id = customers[i].customer_id;
        strncpy(ca->name, customers[i].name, sizeof(ca->name) - 1);
        strncpy(ca->email, customers[i].email, sizeof(ca->email) - 1);
        strncpy(ca->city, customers[i].city, sizeof(ca->city) - 1);
        ca->order_count = order_counts[i];
        ca->total_revenue = revenues[i];
        ca->score = compute_score(ca->order_count, ca->total_revenue);

        summary->analytics_count++;
    }

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
    int print_count;

    if (summary->analytics_count == 0) return;

    print_count = (summary->analytics_count < limit) ? summary->analytics_count : limit;

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
    int customer_count = 0;
    int order_count = 0;
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

    /* Parse customers */
    if (parse_customers_csv(argv[1], customers, &customer_count) != 0) {
        fprintf(stderr, "ERROR: Cannot open customers file: %s\n", argv[1]);
        return 1;
    }

    if (customer_count == 0) {
        fprintf(stderr, "ERROR: No customer records found in file: %s\n", argv[1]);
        return 1;
    }

    printf("  Customers loaded: %d\n", customer_count);

    /* Parse orders */
    if (parse_orders_csv(argv[2], orders, &order_count) != 0) {
        fprintf(stderr, "ERROR: Cannot open orders file: %s\n", argv[2]);
        return 1;
    }

    if (order_count == 0) {
        fprintf(stderr, "ERROR: No order records found in file: %s\n", argv[2]);
        return 1;
    }

    printf("  Orders loaded: %d\n\n", order_count);

    /* Build analytics */
    build_customer_analytics(customers, customer_count, orders, order_count, &summary);

    if (summary.has_error) {
        fprintf(stderr, "ERROR: %s\n", summary.first_error);
        return 1;
    }

    printf("==========================================\n");
    printf("  Customer Score Report\n");
    printf("==========================================\n");
    printf("  Total Customers:    %d\n", summary.customer_count);
    printf("  Total Orders:       %d\n", summary.order_count);
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