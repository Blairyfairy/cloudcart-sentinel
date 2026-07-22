variable "aws_region" { type = string; default = "us-west-2" }
variable "project" { type = string; default = "cloudcart-sentinel" }
variable "environment" { type = string; default = "prod" }
variable "container_image" { type = string }
variable "database_password" { type = string; sensitive = true }
