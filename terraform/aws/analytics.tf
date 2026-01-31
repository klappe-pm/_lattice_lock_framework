resource "aws_s3_bucket" "datalake" {
  bucket = "${var.app_name}-datalake-${var.project_id}-${var.environment}"
}

resource "aws_glue_catalog_database" "glue_db" {
  name = "lattice_lock"
}

# Example Request Logs Table (Partitioned by Date)
resource "aws_glue_catalog_table" "request_logs" {
  name          = "request_logs"
  database_name = aws_glue_catalog_database.glue_db.name

  table_type = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL              = "TRUE"
    "parquet.compression" = "SNAPPY"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.datalake.bucket}/request_logs/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      name                  = "request_logs"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
      parameters = {
        "serialization.format" = "1"
      }
    }

    columns {
      name = "request_id"
      type = "string"
    }
    columns {
      name = "timestamp"
      type = "timestamp"
    }
    columns {
      name = "model"
      type = "string"
    }
    # ... (other columns omitted for brevity, match BigQuery schema)
  }

  partition_keys {
    name = "date"
    type = "date"
  }
}

resource "aws_athena_workgroup" "primary" {
  name = "primary"

  configuration {
    result_configuration {
      output_location = "s3://${aws_s3_bucket.datalake.bucket}/athena-results/"
    }
  }
}
