resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.app_name}-${var.environment}"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", module.db.db_instance_identifier]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Database CPU"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", aws_elasticache_replication_group.cache.replication_group_id]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Cache CPU"
        }
      }
    ]
  })
}
