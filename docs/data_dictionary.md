# Data Dictionary

This document describes the structure and fields of each CSV dataset used by the RetailOps CLI Suite.

---

## 1. sales.csv

Contains individual sales order records. (82 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| order_id | int | Unique order identifier |
| customer_id | int | Customer who placed the order |
| store_id | int | Store where the order was placed |
| product_id | int | Product sold |
| product_name | string | Name of the product |
| category | string | Product category |
| quantity | int | Number of units sold |
| unit_price | float | Price per unit |
| order_date | string | Date of order (YYYY-MM-DD) |
| total_amount | float | Quantity × unit_price |

**Minimum rows:** 80

---

## 2. inventory.csv

Contains current inventory levels for each product. (42 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| product_id | int | Unique product identifier |
| product_name | string | Name of the product |
| category | string | Product category |
| current_stock | int | Units currently in stock |
| reorder_point | int | Stock level triggering reorder |
| unit_cost | float | Cost per unit |
| supplier | string | Supplier name |

**Minimum rows:** 40

---

## 3. customers.csv

Contains customer demographic and registration data. (52 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| customer_id | int | Unique customer identifier |
| name | string | Customer full name |
| email | string | Email address |
| city | string | City of residence |
| signup_date | string | Registration date (YYYY-MM-DD) |

**Minimum rows:** 50

---

## 4. orders.csv

Contains individual order line items with product details. (100 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| order_id | int | Unique order identifier |
| customer_id | int | Customer who placed the order |
| store_id | int | Store where order was placed |
| product_id | int | Product ordered |
| product_name | string | Name of the product |
| category | string | Product category |
| quantity | int | Units ordered |
| unit_price | float | Price per unit |
| order_date | string | Date of order (YYYY-MM-DD) |
| total_amount | float | Quantity × unit_price |

**Minimum rows:** 100

---

## 5. returns.csv

Contains product return records. (28 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| return_id | int | Unique return identifier |
| order_id | int | Original order identifier |
| product_id | int | Product being returned |
| product_name | string | Name of the returned product |
| category | string | Product category |
| quantity | int | Units returned |
| return_amount | float | Total refund amount |
| return_reason | string | Reason for return |
| return_date | string | Return date (YYYY-MM-DD) |

**Minimum rows:** 25

---

## 6. stores.csv

Contains store location and metadata. (14 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| store_id | int | Unique store identifier |
| store_name | string | Store name |
| city | string | City where store is located |
| region | string | Geographic region |
| manager | string | Store manager name |

**Minimum rows:** 12

---

## 7. monthly_revenue.csv

Contains aggregated monthly revenue figures. (36 data rows + header)

| Field | Type | Description |
|-------|------|-------------|
| year | int | Calendar year |
| month | int | Calendar month (1-12) |
| revenue | float | Total revenue for the month |
| total_orders | int | Number of orders placed |
| active_customers | int | Number of active customers |

**Minimum rows:** 36

---

## 8. Generated Reports

When the CLI `report` command is used, a Markdown report is produced containing sections for:

- Sales summary
- Inventory summary
- Customer analysis
- Returns analysis
- Store performance
- Revenue trends

---

## Revision History

| Date | Description |
|------|-------------|
| 2026-06-21 | Initial version |