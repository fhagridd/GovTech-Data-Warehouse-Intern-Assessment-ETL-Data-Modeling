# Sales Data Warehouse Project

Hi! This repository contains my solution for the Data Warehouse Intern Assessment.

My goal was to take raw sales data from a pair of CSV files and build a small, efficient data warehouse. The final product is a clean, query-able database that's ready to power analytics and dashboards. I used Python with the Pandas library for the data processing and SQLite for the database.

## Project Setup and Execution

Follow these instructions to set up and run the project locally.

### Prerequisites

*   Python 3.6+
*   Pandas library

### Installation

1.  Ensure the project folder has the following structure:

    
    project-folder/
    ├── data/
    │   ├── orders.csv
    │   └── products.csv
    └── etl_pipeline.py
    

2. Navigate to the project folder in the terminal and install the pandas library.

    ```bash
    pip install pandas
    ```

### Running the ETL Pipeline

To process the raw data and build the data warehouse, run the following command from the root directory of the project:

```bash
python etl_pipeline.py
```

This will create a new file, `sales_analytics.db`, which is the completed data warehouse.

---

## Task 2: Data Modeling

For this task, I designed a **Star Schema**. I chose this model because it's the industry standard for analytics—it's fast, efficient, and very easy for people to understand and query.

### Schema Overview

*   **`FactSales`**: The central table containing quantitative measures (facts) from sales transactions.
*   **`DimProduct`**: A dimension table storing descriptive attributes of the products.
*   **`DimDate`**: A dimension table storing descriptive attributes of the order dates.

### Table Descriptions

#### `FactSales` (Fact Table)
This table holds the primary records of each sales line item.

| Column    | Data Type | Description                                        | Key            |
| :-------- | :-------- | :------------------------------------------------- | :------------- |
| `OrderID`   | INTEGER   | The unique identifier for an order line item.      | Primary Key  |
| `ProductID` | TEXT      | The foreign key referencing `DimProduct`.          | Foreign Key  |
| `DateID`    | INTEGER   | The foreign key referencing `DimDate`.             | Foreign Key  |
| `Quantity`  | INTEGER   | The number of units sold in the transaction.       |                |
| `Price`     | REAL      | The price per unit at the time of sale.            |                |
| `Revenue`   | REAL      | The calculated total revenue (Quantity * Price).   |                |

#### `DimProduct` (Dimension Table)
These are the "lookup" tables. They hold the context—the "who, what, and when"—for sales numbers.

| Column        | Data Type | Description                              | Key         |
| :------------ | :-------- | :--------------------------------------- | :---------- |
| `ProductID`   | TEXT      | The unique identifier for the product.   | Primary Key |
| `ProductName` | TEXT      | The name of the product.                 |             |
| `Category`    | TEXT      | The category the product belongs to.     |             |

#### `DimDate` (Dimension Table)
This table breaks down the date for easier time-based analysis.

| Column     | Data Type | Description                          | Key         |
| :--------- | :-------- | :----------------------------------- | :---------- |
| `DateID`     | INTEGER   | The unique identifier for the date.  | Primary Key |
| `OrderDate`  | DATE      | The full date of the order.          |             |
| `OrderYear`  | INTEGER   | The year of the order.               |             |
| `OrderMonth` | INTEGER   | The month of the order (1-12).       |             |
| `OrderDay`   | INTEGER   | The day of the month.                |             |

### Relationships
*   `FactSales.ProductID` has a many-to-one relationship with `DimProduct.ProductID`.
*   `FactSales.DateID` has a many-to-one relationship with `DimDate.DateID`.

---

## Task 3: Analytical Query (SQL)

With the data ware house built, the key business question can now be easily answered.

**Business Question:** "What is the total revenue for each product category for each month in the data?"

**SQL Query:**
The following SQL query is run against the `sales_analytics.db` database to answer the question.

```sql
SELECT
    dp.Category,
    dd.OrderMonth,
    SUM(fs.Revenue) AS TotalRevenue
FROM
    FactSales fs
JOIN
    DimProduct dp ON fs.ProductID = dp.ProductID
JOIN
    DimDate dd ON fs.DateID = dd.DateID
GROUP BY
    dp.Category,
    dd.OrderMonth
ORDER BY
    dp.Category,
    dd.OrderMonth;
```

**Query Result:**

| Category    | OrderMonth | TotalRevenue |
| :---------- | :--------- | :----------- |
| Displays    | 1          | 50.0         |
| Peripherals | 1          | 288.0        |

---

## Task 4: Dashboarding Use Case

This section describes how the designed data model supports dashboarding needs and proposes key metrics for a sales performance dashboard.

### How the Data Model Supports Efficient Dashboarding

The star schema is highly effective for dashboarding for three main reasons:

1.  **Simplified Queries:** The separation of facts (numeric values) and dimensions (attributes) makes queries simpler and more intuitive. Dashboard tools can easily generate queries that join the central `FactSales` table with dimension tables, avoiding complex joins on raw, unorganized data.

2.  **Fast Aggregations:** Dashboards primarily display aggregated data (e.g total sales, average quantity). Because the `FactSales` table is narrow and contains pre-calculated numeric data like `Revenue`, the database can perform these aggregations (SUM, COUNT, AVG) very quickly.

3.  **Intuitive Slicing and Dicing:** The dimension tables (`DimProduct`, `DimDate`) act as powerful filters. A business user can easily "slice and dice" the data—for example, filtering total revenue by `Category` from `DimProduct` or by `OrderMonth` from `DimDate`—allowing for interactive exploration of sales performance.

### Proposed Key Metrics and Visualizations

Here are three key metrics and visualizations that would be essential for a sales performance dashboard using this data:

1.  **Total Revenue Over Time (Line Chart)**
    *   **Description:** A line chart showing the `SUM(Revenue)` on the Y-axis and the `OrderDate` on the X-axis.

    *   **Importance:** It's the health check of the business. You can instantly see if sales are trending up or down and spot important patterns.

2.  **Revenue by Product Category (Bar Chart)**
    *   **Description:** A bar chart comparing the `SUM(Revenue)` for each `Category`.

    *   **Importance:** It tells us which parts of our business are the strongest. This helps us decide where to focus our marketing and inventory efforts.

3.  **Top Selling Products (Table)**
    *   **Description:** A sorted table that lists the top 5 or 10 products (`ProductName`) ranked by `SUM(Revenue)` or `SUM(Quantity)`.

    *   **Importance:** This gives us specific, actionable insight. We can see which products customers love the most and make sure they are always in stock.