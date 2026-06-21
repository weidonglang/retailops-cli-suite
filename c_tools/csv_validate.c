/*
 * csv_validate.c
 *
 * RetailOps CLI Suite - CSV Validation Tool
 *
 * Usage: csv_validate.exe <filename> <expected_field_count>
 *
 * Reads a CSV file and validates that each row has the expected number of fields.
 * Outputs total lines, valid lines, and invalid lines.
 *
 * Compile:
 *   gcc c_tools/csv_validate.c -o csv_validate.exe
 *
 * Example:
 *   csv_validate.exe examples/sales.csv 8
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define MAX_LINE_LENGTH 4096
#define MAX_FILENAME_LENGTH 1024
#define MAX_FIELD_COUNT 100

/* Structure to hold validation results */
typedef struct {
    long total_lines;
    long valid_lines;
    long invalid_lines;
    long empty_lines;
    long truncated_lines;
    char first_error[256];
    int has_error;
} ValidationResult;

/* Function prototypes */
int count_fields(const char *line);
int is_empty_line(const char *line);
void trim_trailing_newline(char *line);
ValidationResult validate_csv(const char *filename, int expected_fields);
void print_result(const ValidationResult *result, const char *filename, int expected_fields);
int parse_arguments(int argc, char *argv[], char *filename, int *expected_fields);

/*
 * Count the number of comma-separated fields in a line.
 * Handles quoted fields with embedded commas.
 * Returns the field count, or -1 on error.
 */
int count_fields(const char *line) {
    int count = 0;
    int in_quotes = 0;
    const char *p = line;

    if (line == NULL || *line == '\0') {
        return 0;
    }

    /* Count first field */
    count = 1;

    while (*p) {
        if (*p == '"') {
            in_quotes = !in_quotes;
        } else if (*p == ',' && !in_quotes) {
            count++;
        }
        p++;
    }

    return count;
}

/*
 * Check if a line is empty (only whitespace or newline).
 * Returns 1 if empty, 0 otherwise.
 */
int is_empty_line(const char *line) {
    const char *p = line;
    while (*p) {
        if (!isspace((unsigned char)*p)) {
            return 0;
        }
        p++;
    }
    return 1;
}

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
 * Validate a CSV file.
 * Reads each line, counts fields, and compares to expected count.
 * Returns a ValidationResult struct with summary statistics.
 */
ValidationResult validate_csv(const char *filename, int expected_fields) {
    ValidationResult result;
    FILE *file;
    char line[MAX_LINE_LENGTH];
    long line_number = 0;

    /* Initialize result */
    result.total_lines = 0;
    result.valid_lines = 0;
    result.invalid_lines = 0;
    result.empty_lines = 0;
    result.truncated_lines = 0;
    result.first_error[0] = '\0';
    result.has_error = 0;

    /* Open file */
    file = fopen(filename, "r");
    if (file == NULL) {
        snprintf(result.first_error, sizeof(result.first_error),
                 "Cannot open file: %s", filename);
        result.has_error = 1;
        return result;
    }

    /* Read and validate each line */
    while (fgets(line, sizeof(line), file) != NULL) {
        int fields;
        size_t line_len;
        line_number++;

        trim_trailing_newline(line);

        /* Skip empty lines */
        if (is_empty_line(line)) {
            result.empty_lines++;
            continue;
        }

        /* Check for truncated lines (buffer full without newline) */
        line_len = strlen(line);
        if (line_len >= MAX_LINE_LENGTH - 1) {
            result.truncated_lines++;
            result.invalid_lines++;
            if (result.first_error[0] == '\0') {
                snprintf(result.first_error, sizeof(result.first_error),
                         "Line %ld: line too long (truncated at %d chars)",
                         line_number, MAX_LINE_LENGTH - 1);
            }
            continue;
        }

        result.total_lines++;

        fields = count_fields(line);

        /* Sanity check: unreasonably large field count */
        if (fields > MAX_FIELD_COUNT) {
            result.invalid_lines++;
            if (result.first_error[0] == '\0') {
                snprintf(result.first_error, sizeof(result.first_error),
                         "Line %ld: field count %d exceeds sanity limit %d",
                         line_number, fields, MAX_FIELD_COUNT);
            }
            continue;
        }

        if (fields == expected_fields) {
            result.valid_lines++;
        } else {
            result.invalid_lines++;
            if (result.first_error[0] == '\0') {
                snprintf(result.first_error, sizeof(result.first_error),
                         "Line %ld: expected %d fields, got %d",
                         line_number, expected_fields, fields);
            }
        }
    }

    /* Check for read error */
    if (ferror(file)) {
        snprintf(result.first_error, sizeof(result.first_error),
                 "Error reading file: %s", filename);
        result.has_error = 1;
    }

    fclose(file);
    return result;
}

/*
 * Print the validation results in a formatted table.
 */
void print_result(const ValidationResult *result, const char *filename, int expected_fields) {
    printf("========================================\n");
    printf("  CSV Validation Report\n");
    printf("========================================\n");
    printf("  File:              %s\n", filename);
    printf("  Expected Fields:   %d\n", expected_fields);
    printf("----------------------------------------\n");
    printf("  Total Data Lines:  %ld\n", result->total_lines);
    printf("  Valid Lines:       %ld\n", result->valid_lines);
    printf("  Invalid Lines:     %ld\n", result->invalid_lines);
    printf("  Empty Lines:       %ld\n", result->empty_lines);
    printf("  Truncated Lines:   %ld\n", result->truncated_lines);
    printf("----------------------------------------\n");

    if (result->total_lines > 0) {
        double valid_pct = (double)result->valid_lines / result->total_lines * 100.0;
        double invalid_pct = (double)result->invalid_lines / result->total_lines * 100.0;
        printf("  Valid Rate:        %.1f%%\n", valid_pct);
        printf("  Invalid Rate:      %.1f%%\n", invalid_pct);
    }

    printf("========================================\n");

    if (result->invalid_lines > 0 && result->first_error[0] != '\0') {
        printf("\n  FIRST ERROR:\n");
        printf("    %s\n", result->first_error);
    }

    if (result->has_error) {
        printf("\n  ERROR: %s\n", result->first_error);
    }
}

/*
 * Parse command-line arguments.
 * Returns 0 on success, 1 on error.
 */
int parse_arguments(int argc, char *argv[], char *filename, int *expected_fields) {
    if (argc < 3) {
        fprintf(stderr, "ERROR: Insufficient arguments.\n");
        fprintf(stderr, "Usage: %s <filename> <expected_field_count>\n",
                argv[0] ? argv[0] : "csv_validate");
        fprintf(stderr, "Example: %s examples/sales.csv 8\n",
                argv[0] ? argv[0] : "csv_validate");
        return 1;
    }

    /* Check filename length */
    if (strlen(argv[1]) >= MAX_FILENAME_LENGTH) {
        fprintf(stderr, "ERROR: Filename too long (max %d characters).\n",
                MAX_FILENAME_LENGTH - 1);
        return 1;
    }

    strncpy(filename, argv[1], MAX_FILENAME_LENGTH - 1);
    filename[MAX_FILENAME_LENGTH - 1] = '\0';

    /* Parse expected field count */
    *expected_fields = atoi(argv[2]);
    if (*expected_fields <= 0) {
        fprintf(stderr, "ERROR: Invalid expected field count: '%s'\n", argv[2]);
        fprintf(stderr, "       Expected field count must be a positive integer.\n");
        return 1;
    }

    return 0;
}

/*
 * Main entry point.
 * Parses arguments, validates the CSV file, and prints results.
 */
int main(int argc, char *argv[]) {
    char filename[MAX_FILENAME_LENGTH];
    int expected_fields;
    ValidationResult result;

    printf("CSV Validation Tool - RetailOps CLI Suite\n");
    printf("========================================\n\n");

    /* Parse command-line arguments */
    if (parse_arguments(argc, argv, filename, &expected_fields) != 0) {
        return 1;
    }

    printf("Validating: %s (expecting %d fields per row)\n\n",
           filename, expected_fields);

    /* Validate the CSV file */
    result = validate_csv(filename, expected_fields);

    /* Check for file open errors */
    if (result.has_error && result.total_lines == 0 && result.valid_lines == 0) {
        fprintf(stderr, "ERROR: %s\n", result.first_error);
        return 1;
    }

    /* Warn if file has no data lines (possibly all headers or empty) */
    if (result.total_lines == 0) {
        fprintf(stderr, "ERROR: No data lines found in file: %s\n", filename);
        return 1;
    }

    /* Print results */
    print_result(&result, filename, expected_fields);

    /* Return non-zero exit code if there are invalid lines */
    if (result.invalid_lines > 0) {
        return 1;
    }

    printf("\nValidation complete.\n");
    return 0;
}