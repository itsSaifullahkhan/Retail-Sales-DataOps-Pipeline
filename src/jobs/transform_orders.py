import csv
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    explode,
    round as spark_round,
    sum as spark_sum,
)


RAW_DATA_PATH = "data/raw/carts.json"

OUTPUT_PATH = Path("data/output/sales_report")
FINAL_CSV_FILE = OUTPUT_PATH / "final_sales_report.csv"


def create_spark_session():
    """
    Create Spark session.

    SparkSession is the main entry point for working with PySpark.
    """
    spark = (
        SparkSession.builder
        .appName("ApiRetailSalesETL")
        .master("local[*]")
        .getOrCreate()
    )

    return spark


def transform_carts(raw_df):
    """
    Transform nested carts API JSON data into a clean sales report.

    API JSON structure:
    carts
      └── products

    We use explode() because carts and products are nested arrays.
    """

    # Step 1: Convert carts array into separate rows
    carts_df = raw_df.select(
        explode(col("carts")).alias("cart")
    )

    # Step 2: Convert products array inside each cart into separate rows
    products_df = carts_df.select(
        col("cart.id").alias("cart_id"),
        col("cart.userId").alias("user_id"),
        explode(col("cart.products")).alias("product")
    )

    # Step 3: Flatten nested product fields into normal table columns
    flattened_df = products_df.select(
        col("cart_id"),
        col("user_id"),
        col("product.id").alias("product_id"),
        col("product.title").alias("product_name"),
        col("product.price").alias("price"),
        col("product.quantity").alias("quantity"),
        col("product.total").alias("total_amount"),
        col("product.discountPercentage").alias("discount_percentage"),
        col("product.discountedTotal").alias("discounted_total")
    )

    # Step 4: Remove rows having missing values
    cleaned_df = flattened_df.dropna()

    # Step 5: Create final product-level sales report
    sales_report_df = cleaned_df.groupBy("product_name").agg(
        count("cart_id").alias("total_orders"),
        spark_sum("quantity").alias("total_quantity_sold"),
        spark_round(spark_sum("total_amount"), 2).alias("gross_sales"),
        spark_round(spark_sum("discounted_total"), 2).alias("net_sales_after_discount")
    )

    return sales_report_df


def save_report_as_csv(df, file_path):
    """
    Save Spark DataFrame as one normal CSV file.

    Spark normally saves output as folders with part files.
    On Windows, Spark can also give winutils/HADOOP_HOME errors while writing.

    For this beginner project, we collect the small final report
    and save it as a clean CSV file using normal Python.
    """

    file_path.parent.mkdir(parents=True, exist_ok=True)

    rows = df.collect()
    columns = df.columns

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header
        writer.writerow(columns)

        # Write data rows
        for row in rows:
            writer.writerow([row[column] for column in columns])


def main():
    spark = create_spark_session()

    print("Reading raw JSON data...")

    raw_df = spark.read.option("multiLine", "true").json(RAW_DATA_PATH)

    print("Transforming carts data...")

    final_report_df = transform_carts(raw_df)

    print("Final sales report:")

    final_report_df.show(50, truncate=False)

    print("Saving output as single CSV file...")

    save_report_as_csv(final_report_df, FINAL_CSV_FILE)

    print(f"CSV output saved successfully at: {FINAL_CSV_FILE}")

    spark.stop()


if __name__ == "__main__":
    main()