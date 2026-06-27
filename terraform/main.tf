terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "4.4.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "spark_image" {
  name         = "apache/spark:3.5.1-java17-python3"
  keep_locally = true
}

resource "docker_container" "spark_etl" {
  name     = "api_retail_spark_etl_tf"
  image    = docker_image.spark_image.image_id
  user     = "root"
  must_run = false

  working_dir = "/app"

  volumes {
    host_path      = abspath("${path.module}/..")
    container_path = "/app"
  }

  command = [
    "bash",
    "-lc",
    "/opt/spark/bin/spark-submit src/jobs/transform_orders.py"
  ]
}