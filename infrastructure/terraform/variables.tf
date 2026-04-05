variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for the FOD-WPT API server"
  type        = string
  default     = "t3.small"
}

variable "key_pair_name" {
  description = "Name of the existing EC2 key pair used for SSH access"
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name for model artifacts and drift reports"
  type        = string
  default     = "fod-wpt-mlops-artifacts"
}
