# Lattice Lock GCP Infrastructure Variables

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "development"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

# Cloud SQL
variable "sql_tier" {
  description = "Cloud SQL machine tier"
  type        = string
  default     = "db-custom-2-8192"  # 2 vCPU, 8GB RAM
}

variable "sql_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 20
}

# Firestore
variable "firestore_location" {
  description = "Firestore database location"
  type        = string
  default     = "us-central"
}

# Redis
variable "redis_memory_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
}
