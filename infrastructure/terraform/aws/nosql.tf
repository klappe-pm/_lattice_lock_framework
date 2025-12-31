resource "aws_dynamodb_table" "sessions" {
  name           = "sessions-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "userId"
    type = "S"
  }

  attribute {
    name = "lastActivityAt"
    type = "S" # ISO timestamp as string
  }

  attribute {
    name = "organizationId"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  # Index: sessions_by_user (matches GCP: userId ASC, lastActivityAt DESC)
  global_secondary_index {
    name               = "sessions_by_user"
    hash_key           = "userId"
    range_key          = "lastActivityAt"
    projection_type    = "ALL"
  }

  # Index: sessions_by_org (matches GCP: organizationId ASC, status ASC)
  global_secondary_index {
    name               = "sessions_by_org"
    hash_key           = "organizationId"
    range_key          = "status"
    projection_type    = "ALL"
  }

  point_in_time_recovery {
    enabled = var.environment == "prod"
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Environment = var.environment
  }
}
