import json
import sys
from pathlib import Path
from pyspark.sql import SparkSession

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.jobs.transform_orders import transform_carts


def test_transform_carts(tmp_path):
    """
    Test that transform_carts correctly calculates sales metrics.
    """

    spark = (
        SparkSession.builder
        .appName("TestApiRetailSalesETL")
        .master("local[*]")
        .getOrCreate()
    )

    sample_data = {
        "carts": [
            {
                "id": 1,
                "userId": 101,
                "products": [
                    {
                        "id": 1,
                        "title": "Laptop",
                        "price": 1000,
                        "quantity": 2,
                        "total": 2000,
                        "discountPercentage": 10,
                        "discountedTotal": 1800
                    },
                    {
                        "id": 2,
                        "title": "Mouse",
                        "price": 50,
                        "quantity": 3,
                        "total": 150,
                        "discountPercentage": 0,
                        "discountedTotal": 150
                    }
                ]
            }
        ],
        "total": 1,
        "skip": 0,
        "limit": 1
    }

    test_json_path = tmp_path / "sample_carts.json"

    with open(test_json_path, "w", encoding="utf-8") as file:
        json.dump(sample_data, file)

    raw_df = spark.read.option("multiLine", "true").json(str(test_json_path))

    result_df = transform_carts(raw_df)

    result = {
        row["product_name"]: row.asDict()
        for row in result_df.collect()
    }

    assert result["Laptop"]["total_orders"] == 1
    assert result["Laptop"]["total_quantity_sold"] == 2
    assert result["Laptop"]["gross_sales"] == 2000
    assert result["Laptop"]["net_sales_after_discount"] == 1800

    assert result["Mouse"]["total_orders"] == 1
    assert result["Mouse"]["total_quantity_sold"] == 3
    assert result["Mouse"]["gross_sales"] == 150
    assert result["Mouse"]["net_sales_after_discount"] == 150

    spark.stop()