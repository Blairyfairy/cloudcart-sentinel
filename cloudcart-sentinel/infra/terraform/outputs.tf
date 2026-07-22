output "load_balancer_dns" { value = aws_lb.main.dns_name }
output "database_endpoint" { value = aws_db_instance.postgres.address; sensitive = true }
