# Lattice Lock GCP Infrastructure
# Terraform configuration for database services

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "lattice-lock-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ==============================================================================
# VPC Network
# ==============================================================================

resource "google_compute_network" "main" {
  name                    = "lattice-lock-network"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "main" {
  name          = "lattice-lock-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  
  private_ip_google_access = true
}

resource "google_compute_global_address" "private_ip" {
  name          = "lattice-lock-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip.name]
}

# ==============================================================================
# Cloud SQL (PostgreSQL)
# ==============================================================================

resource "google_sql_database_instance" "main" {
  name             = "lattice-lock-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  
  depends_on = [google_service_networking_connection.private_vpc]
  
  settings {
    tier              = var.sql_tier
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_size         = var.sql_disk_size
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = var.environment == "production"
      start_time                     = "03:00"
      transaction_log_retention_days = 7
      
      backup_retention_settings {
        retained_backups = var.environment == "production" ? 30 : 7
        retention_unit   = "COUNT"
      }
    }
    
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = google_compute_network.main.id
      enable_private_path_for_google_cloud_services = true
    }
    
    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }
    
    database_flags {
      name  = "max_connections"
      value = "200"
    }
    
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 4096
      record_application_tags = true
      record_client_address   = true
    }
    
    maintenance_window {
      day          = 7  # Sunday
      hour         = 4  # 4 AM
      update_track = "stable"
    }
  }
  
  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "main" {
  name     = "lattice_lock"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "app" {
  name     = "lattice_lock_app"
  instance = google_sql_database_instance.main.name
  password = random_password.sql_password.result
}

resource "random_password" "sql_password" {
  length  = 32
  special = true
}

# Store password in Secret Manager
resource "google_secret_manager_secret" "sql_password" {
  secret_id = "lattice-lock-sql-password"
  
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "sql_password" {
  secret      = google_secret_manager_secret.sql_password.id
  secret_data = random_password.sql_password.result
}

# ==============================================================================
# Firestore
# ==============================================================================

resource "google_firestore_database" "main" {
  provider    = google-beta
  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"
  
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
}

# Firestore indexes for common queries
resource "google_firestore_index" "sessions_by_user" {
  provider   = google-beta
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "sessions"
  
  fields {
    field_path = "userId"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "lastActivityAt"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "sessions_by_org" {
  provider   = google-beta
  project    = var.project_id
  database   = google_firestore_database.main.name
  collection = "sessions"
  
  fields {
    field_path = "organizationId"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "status"
    order      = "ASCENDING"
  }
}

# ==============================================================================
# BigQuery
# ==============================================================================

resource "google_bigquery_dataset" "main" {
  dataset_id  = "lattice_lock"
  description = "Lattice Lock analytics and audit data"
  location    = var.region
  
  default_table_expiration_ms = null
  
  labels = {
    environment = var.environment
  }
}

resource "google_bigquery_table" "request_logs" {
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "request_logs"
  deletion_protection = var.environment == "production"
  
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
  
  clustering = ["organization_id", "user_id", "model"]
  
  schema = jsonencode([
    { name = "request_id", type = "STRING", mode = "REQUIRED" },
    { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "user_id", type = "STRING", mode = "NULLABLE" },
    { name = "organization_id", type = "STRING", mode = "NULLABLE" },
    { name = "api_key_id", type = "STRING", mode = "NULLABLE" },
    { name = "session_id", type = "STRING", mode = "NULLABLE" },
    { name = "model", type = "STRING", mode = "REQUIRED" },
    { name = "provider", type = "STRING", mode = "REQUIRED" },
    { name = "prompt_tokens", type = "INT64", mode = "NULLABLE" },
    { name = "completion_tokens", type = "INT64", mode = "NULLABLE" },
    { name = "total_tokens", type = "INT64", mode = "NULLABLE" },
    { name = "latency_ms", type = "INT64", mode = "NULLABLE" },
    { name = "time_to_first_token_ms", type = "INT64", mode = "NULLABLE" },
    { name = "estimated_cost", type = "FLOAT64", mode = "NULLABLE" },
    { name = "status", type = "STRING", mode = "NULLABLE" },
    { name = "error_code", type = "STRING", mode = "NULLABLE" },
    { name = "error_message", type = "STRING", mode = "NULLABLE" },
    { name = "chain_id", type = "STRING", mode = "NULLABLE" },
    { name = "step_number", type = "INT64", mode = "NULLABLE" },
    { name = "is_consensus", type = "BOOL", mode = "NULLABLE" },
    { name = "consensus_score", type = "FLOAT64", mode = "NULLABLE" },
    { name = "client_ip", type = "STRING", mode = "NULLABLE" },
    { name = "user_agent", type = "STRING", mode = "NULLABLE" },
    { name = "request_metadata", type = "JSON", mode = "NULLABLE" },
    { name = "response_metadata", type = "JSON", mode = "NULLABLE" },
  ])
}

resource "google_bigquery_table" "audit_events" {
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "audit_events"
  deletion_protection = var.environment == "production"
  
  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
  
  clustering = ["organization_id", "event_type"]
  
  schema = jsonencode([
    { name = "event_id", type = "STRING", mode = "REQUIRED" },
    { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "user_id", type = "STRING", mode = "NULLABLE" },
    { name = "api_key_id", type = "STRING", mode = "NULLABLE" },
    { name = "ip_address", type = "STRING", mode = "NULLABLE" },
    { name = "user_agent", type = "STRING", mode = "NULLABLE" },
    { name = "event_type", type = "STRING", mode = "REQUIRED" },
    { name = "resource_type", type = "STRING", mode = "NULLABLE" },
    { name = "resource_id", type = "STRING", mode = "NULLABLE" },
    { name = "action", type = "STRING", mode = "NULLABLE" },
    { name = "previous_state", type = "JSON", mode = "NULLABLE" },
    { name = "new_state", type = "JSON", mode = "NULLABLE" },
    { name = "organization_id", type = "STRING", mode = "NULLABLE" },
    { name = "session_id", type = "STRING", mode = "NULLABLE" },
    { name = "request_id", type = "STRING", mode = "NULLABLE" },
  ])
}

resource "google_bigquery_table" "daily_usage" {
  dataset_id          = google_bigquery_dataset.main.dataset_id
  table_id            = "daily_usage"
  deletion_protection = var.environment == "production"
  
  time_partitioning {
    type  = "DAY"
    field = "date"
  }
  
  clustering = ["organization_id", "model"]
  
  schema = jsonencode([
    { name = "date", type = "DATE", mode = "REQUIRED" },
    { name = "organization_id", type = "STRING", mode = "REQUIRED" },
    { name = "user_id", type = "STRING", mode = "NULLABLE" },
    { name = "model", type = "STRING", mode = "REQUIRED" },
    { name = "provider", type = "STRING", mode = "REQUIRED" },
    { name = "request_count", type = "INT64", mode = "NULLABLE" },
    { name = "total_input_tokens", type = "INT64", mode = "NULLABLE" },
    { name = "total_output_tokens", type = "INT64", mode = "NULLABLE" },
    { name = "total_cost", type = "FLOAT64", mode = "NULLABLE" },
    { name = "avg_latency_ms", type = "FLOAT64", mode = "NULLABLE" },
    { name = "p50_latency_ms", type = "FLOAT64", mode = "NULLABLE" },
    { name = "p95_latency_ms", type = "FLOAT64", mode = "NULLABLE" },
    { name = "p99_latency_ms", type = "FLOAT64", mode = "NULLABLE" },
    { name = "error_count", type = "INT64", mode = "NULLABLE" },
    { name = "timeout_count", type = "INT64", mode = "NULLABLE" },
  ])
}

# ==============================================================================
# Memorystore (Redis)
# ==============================================================================

resource "google_redis_instance" "cache" {
  name           = "lattice-lock-cache-${var.environment}"
  tier           = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb = var.redis_memory_gb
  region         = var.region
  
  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  
  redis_version = "REDIS_7_0"
  
  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }
  
  labels = {
    environment = var.environment
  }
  
  depends_on = [google_service_networking_connection.private_vpc]
}

# ==============================================================================
# Cloud KMS (for encryption)
# ==============================================================================

resource "google_kms_key_ring" "main" {
  name     = "lattice-lock-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "database" {
  name     = "database-encryption-key"
  key_ring = google_kms_key_ring.main.id
  purpose  = "ENCRYPT_DECRYPT"
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "google_kms_crypto_key" "secrets" {
  name     = "secrets-encryption-key"
  key_ring = google_kms_key_ring.main.id
  purpose  = "ENCRYPT_DECRYPT"
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# ==============================================================================
# Outputs
# ==============================================================================

output "sql_connection_name" {
  value       = google_sql_database_instance.main.connection_name
  description = "Cloud SQL connection name for Cloud Run"
}

output "sql_private_ip" {
  value       = google_sql_database_instance.main.private_ip_address
  description = "Cloud SQL private IP address"
}

output "redis_host" {
  value       = google_redis_instance.cache.host
  description = "Redis instance host"
}

output "redis_port" {
  value       = google_redis_instance.cache.port
  description = "Redis instance port"
}

output "bigquery_dataset" {
  value       = google_bigquery_dataset.main.dataset_id
  description = "BigQuery dataset ID"
}

output "kms_key_database" {
  value       = google_kms_crypto_key.database.id
  description = "KMS key for database encryption"
}
