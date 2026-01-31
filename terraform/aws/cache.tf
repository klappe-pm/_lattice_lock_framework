resource "aws_elasticache_replication_group" "cache" {
  replication_group_id          = "${var.app_name}-cache-${var.environment}"
  description                   = "Redis Cache for Lattice Lock"
  node_type                     = var.elasticache_node_type
  port                          = 6379
  parameter_group_name          = "default.redis7"
  snapshot_retention_limit      = var.environment == "prod" ? 7 : 0
  automatic_failover_enabled    = var.environment == "prod"
  
  num_cache_clusters            = var.environment == "prod" ? 2 : 1
  multi_az_enabled              = var.environment == "prod"
  
  subnet_group_name             = aws_elasticache_subnet_group.cache.name
  security_group_ids            = [module.cache_sg.security_group_id]
  
  at_rest_encryption_enabled    = true
  transit_encryption_enabled    = true
  auth_token                    = random_password.redis_auth_token.result
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_elasticache_subnet_group" "cache" {
  name       = "${var.app_name}-cache-subnet-${var.environment}"
  subnet_ids = module.vpc.private_subnets # Typically cache serves app in private subnets
}

module "cache_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-cache-sg-${var.environment}"
  description = "Redis security group"
  vpc_id      = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 6379
      to_port     = 6379
      protocol    = "tcp"
      description = "Redis access from within VPC"
      cidr_blocks = module.vpc.vpc_cidr_block
    },
  ]
}

resource "random_password" "redis_auth_token" {
  length           = 32
  special          = false
}

resource "aws_secretsmanager_secret" "redis_auth" {
  name        = "${var.app_name}-redis-auth-${var.environment}"
  description = "Redis AUTH token"
}

resource "aws_secretsmanager_secret_version" "redis_auth" {
  secret_id     = aws_secretsmanager_secret.redis_auth.id
  secret_string = random_password.redis_auth_token.result
}
