module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.app_name}-db-${var.environment}"

  engine               = "postgres"
  engine_version       = "15.4"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = "lattice_lock"
  username = "lattice_lock_app"
  port     = 5432

  multi_az               = var.environment == "prod"
  subnet_ids             = module.vpc.database_subnets
  vpc_security_group_ids = [module.db_sg.security_group_id]

  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  create_cloudwatch_log_group     = true

  backup_retention_period = var.environment == "prod" ? 30 : 7
  skip_final_snapshot     = var.environment != "prod"
  deletion_protection     = var.environment == "prod"

  performance_insights_enabled = true
  create_monitoring_role       = true
  monitoring_interval          = 60

  parameters = [
    {
      name  = "log_min_duration_statement"
      value = 1000
    },
    {
        name = "rds.force_ssl"
        value = 1
    }
  ]

  tags = {
    Environment = var.environment
  }
}

module "db_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-db-sg-${var.environment}"
  description = "PostgreSQL security group"
  vpc_id      = module.vpc.vpc_id

  # Ingress from VPC CIDR (typically app subnets)
  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "PostgreSQL access from within VPC"
      cidr_blocks = module.vpc.vpc_cidr_block
    },
  ]
}

resource "aws_secretsmanager_secret" "db_password" {
  name        = "${var.app_name}-db-password-${var.environment}"
  description = "Password for RDS instance"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = module.db.db_instance_username
    password = module.db.db_instance_password
    engine   = "postgres"
    host     = module.db.db_instance_address
    port     = module.db.db_instance_port
    dbname   = module.db.db_instance_name
  })
}
