import pandas as pd
import sqlite3

def extract_data(orders_path, products_path):
    #Reads CSV files and takes file paths and returns data
    orders_df = pd.read_csv(orders_path)
    products_df = pd.read_csv(products_path)
    return orders_df, products_df

#Cleans and prepare raw data, takes read data and get ready for the database

def transform_data(orders_df, products_df):

    #Create a new 'Revenue' column by multiplying how many items were sold (Quantity)
    orders_df['Revenue'] = orders_df['Quantity'] * orders_df['Price']

    #Change OrderDate from plain text into a real date that can be worked with
    orders_df['OrderDate'] = pd.to_datetime(orders_df['OrderDate'])
    #Extract year,month, and day from the full date into their own columns
    orders_df['OrderYear'] = orders_df['OrderDate'].dt.year
    orders_df['OrderMonth'] = orders_df['OrderDate'].dt.month
    orders_df['OrderDay'] = orders_df['OrderDate'].dt.day

    #Combine the orders data with the products data using the 'ProductID' column, adds useful details like 'ProductName' and  'Category' to each sale.
    merged_df = pd.merge(orders_df, products_df, on='ProductID')
    return merged_df


#Saves prepared data into SQLite database, creates the tables and loads the data into them.
def load_data(df, db_path):
   
    #Create our products lookup table, lists of all products
    dim_product = df[['ProductID', 'ProductName', 'Category']].drop_duplicates().reset_index(drop=True)
    
    #Create 'Date' lookup table.lists all dates sales occured on
    dim_date = df[['OrderDate', 'OrderYear', 'OrderMonth', 'OrderDay']].drop_duplicates().reset_index(drop=True)
    
    #Give each unique date a simpler number ID
    dim_date['DateID'] = dim_date.index

    #Creates main 'Sales' table, holds all numbers like Quantity and revenue. Uses IDs from looup tables instead of repeating all details.
    fact_sales = pd.merge(df, dim_date, on='OrderDate') # add the new 'DateID' to sales data
    
    #Select only columns needed for final sales table
    fact_sales = fact_sales[['OrderID', 'ProductID', 'DateID', 'Quantity', 'Price', 'Revenue']]

    #Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #Drop old tables before  starting, ensures a fresh start
    cursor.execute("DROP TABLE IF EXISTS DimProduct")
    cursor.execute("DROP TABLE IF EXISTS DimDate")
    cursor.execute("DROP TABLE IF EXISTS FactSales")

    #Create tables in database
    cursor.execute('''
    CREATE TABLE DimProduct (
        ProductID TEXT PRIMARY KEY,
        ProductName TEXT,
        Category TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE DimDate (
        DateID INTEGER PRIMARY KEY,
        OrderDate DATE,
        OrderYear INTEGER,
        OrderMonth INTEGER,
        OrderDay INTEGER
    )
    ''')
    cursor.execute('''
    CREATE TABLE FactSales (
        OrderID INTEGER,
        ProductID TEXT,
        DateID INTEGER,
        Quantity INTEGER,
        Price REAL,
        Revenue REAL,
        PRIMARY KEY (OrderID, ProductID),
        FOREIGN KEY (ProductID) REFERENCES DimProduct(ProductID),
        FOREIGN KEY (DateID) REFERENCES DimDate(DateID)
    )
    ''')

    #This section loads data into tables
    dim_product.to_sql('DimProduct', conn, if_exists='append', index=False)
    dim_date.to_sql('DimDate', conn, if_exists='append', index=False)
    fact_sales.to_sql('FactSales', conn, if_exists='append', index=False)


    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    orders_file = 'data/orders.csv'
    products_file = 'data/products.csv'
    database_file = 'sales_analytics.db'

    
    orders, products = extract_data(orders_file, products_file)

    transformed_data = transform_data(orders, products)

    load_data(transformed_data, database_file)
    print(f"ETL process completed. Data loaded into {database_file}")