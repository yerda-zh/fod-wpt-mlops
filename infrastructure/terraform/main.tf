terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.6"
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------------------------
# S3 — model artifacts and drift reports
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "artifacts" {
  bucket = var.bucket_name

  tags = {
    Project = "fod-wpt-mlops"
  }
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ---------------------------------------------------------------------------
# ECR — Docker image repository
# ---------------------------------------------------------------------------

resource "aws_ecr_repository" "api" {
  name                 = "fod-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = "fod-wpt-mlops"
  }
}

# ---------------------------------------------------------------------------
# Security group
# ---------------------------------------------------------------------------

resource "aws_security_group" "fod_api" {
  name        = "fod-api-sg"
  description = "FOD-WPT API server — allow SSH, HTTP, API, Grafana, Prometheus"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP (nginx / frontend)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "FastAPI"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = "fod-wpt-mlops"
  }
}

# ---------------------------------------------------------------------------
# EC2 — Ubuntu 24.04 LTS (us-east-1 HVM SSD AMI)
# Key pair: var.key_pair_name must already exist in the target AWS account.
# ---------------------------------------------------------------------------

resource "aws_instance" "api" {
  # Ubuntu 24.04 LTS — us-east-1 (update AMI ID if deploying to another region)
  ami                    = "ami-0c7217cdde317cfec"
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.fod_api.id]

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name    = "fod-wpt-api"
    Project = "fod-wpt-mlops"
  }
}

# ---------------------------------------------------------------------------
# Elastic IP
# ---------------------------------------------------------------------------

resource "aws_eip" "api" {
  instance = aws_instance.api.id
  domain   = "vpc"

  tags = {
    Project = "fod-wpt-mlops"
  }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "elastic_ip" {
  description = "Public Elastic IP of the API server"
  value       = aws_eip.api.public_ip
}

output "ecr_repository_url" {
  description = "ECR repository URL for docker push"
  value       = aws_ecr_repository.api.repository_url
}

output "s3_bucket_name" {
  description = "S3 bucket for model artifacts and drift reports"
  value       = aws_s3_bucket.artifacts.bucket
}
