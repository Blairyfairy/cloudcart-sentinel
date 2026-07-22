data "aws_availability_zones" "available" { state = "available" }
locals { name = "${var.project}-${var.environment}" }

resource "aws_vpc" "main" {
  cidr_block = "10.20.0.0/16"
  enable_dns_hostnames = true
  tags = { Name = local.name }
}
resource "aws_subnet" "public" {
  count = 2
  vpc_id = aws_vpc.main.id
  cidr_block = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${local.name}-public-${count.index}" }
}
resource "aws_internet_gateway" "main" { vpc_id = aws_vpc.main.id }
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route { cidr_block = "0.0.0.0/0"; gateway_id = aws_internet_gateway.main.id }
}
resource "aws_route_table_association" "public" {
  count = 2
  subnet_id = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
resource "aws_security_group" "alb" {
  name = "${local.name}-alb"; vpc_id = aws_vpc.main.id
  ingress { from_port=80; to_port=80; protocol="tcp"; cidr_blocks=["0.0.0.0/0"] }
  egress { from_port=0; to_port=0; protocol="-1"; cidr_blocks=["0.0.0.0/0"] }
}
resource "aws_security_group" "app" {
  name = "${local.name}-app"; vpc_id = aws_vpc.main.id
  ingress { from_port=8000; to_port=8000; protocol="tcp"; security_groups=[aws_security_group.alb.id] }
  egress { from_port=0; to_port=0; protocol="-1"; cidr_blocks=["0.0.0.0/0"] }
}
resource "aws_lb" "main" {
  name = substr(local.name,0,32); internal=false; load_balancer_type="application"
  security_groups=[aws_security_group.alb.id]; subnets=aws_subnet.public[*].id
}
resource "aws_lb_target_group" "api" {
  name=substr("${local.name}-api",0,32); port=8000; protocol="HTTP"; vpc_id=aws_vpc.main.id; target_type="ip"
  health_check { path="/health/ready"; matcher="200" }
}
resource "aws_lb_listener" "http" {
  load_balancer_arn=aws_lb.main.arn; port=80; protocol="HTTP"
  default_action { type="forward"; target_group_arn=aws_lb_target_group.api.arn }
}
resource "aws_ecs_cluster" "main" { name=local.name }
resource "aws_iam_role" "task_execution" {
  name="${local.name}-execution"
  assume_role_policy=jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy_attachment" "execution" { role=aws_iam_role.task_execution.name; policy_arn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" }
resource "aws_cloudwatch_log_group" "api" { name="/ecs/${local.name}"; retention_in_days=30 }
resource "aws_ecs_task_definition" "api" {
  family=local.name; network_mode="awsvpc"; requires_compatibilities=["FARGATE"]; cpu=512; memory=1024
  execution_role_arn=aws_iam_role.task_execution.arn
  container_definitions=jsonencode([{name="api",image=var.container_image,essential=true,portMappings=[{containerPort=8000}],logConfiguration={logDriver="awslogs",options={"awslogs-group"=aws_cloudwatch_log_group.api.name,"awslogs-region"=var.aws_region,"awslogs-stream-prefix"="api"}}}])
}
resource "aws_ecs_service" "api" {
  name=local.name; cluster=aws_ecs_cluster.main.id; task_definition=aws_ecs_task_definition.api.arn; desired_count=2; launch_type="FARGATE"
  network_configuration { subnets=aws_subnet.public[*].id; security_groups=[aws_security_group.app.id]; assign_public_ip=true }
  load_balancer { target_group_arn=aws_lb_target_group.api.arn; container_name="api"; container_port=8000 }
  depends_on=[aws_lb_listener.http]
}
resource "aws_db_subnet_group" "main" { name=local.name; subnet_ids=aws_subnet.public[*].id }
resource "aws_db_instance" "postgres" {
  identifier=local.name; engine="postgres"; engine_version="16.3"; instance_class="db.t4g.micro"; allocated_storage=20
  db_name="sentinel"; username="sentinel"; password=var.database_password; db_subnet_group_name=aws_db_subnet_group.main.name
  vpc_security_group_ids=[aws_security_group.app.id]; storage_encrypted=true; backup_retention_period=7; skip_final_snapshot=true
}
