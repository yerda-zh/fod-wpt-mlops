# FOD-WPT MLOps — Terraform

Provisions the AWS infrastructure for the FOD-WPT API:

| Resource | Details |
|---|---|
| S3 bucket | Model artifacts + drift reports (`fod-wpt-mlops-artifacts`) |
| ECR repository | Docker images (`fod-api`) |
| EC2 instance | Ubuntu 22.04, `t3.small`, 20 GB gp3 |
| Elastic IP | Static public IP associated with the EC2 instance |
| Security group | Ingress on 22, 80, 8000, 3000, 9090 |

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.6
- AWS credentials configured (`aws configure` or environment variables)
- An existing EC2 key pair in your target AWS account

## Usage

```bash
cd infrastructure/terraform

# 1. Initialise providers
terraform init

# 2. Preview changes
terraform plan -var="key_pair_name=<your-key-pair>"

# 3. Apply
terraform apply -var="key_pair_name=<your-key-pair>"
```

Terraform will print the `elastic_ip`, `ecr_repository_url`, and `s3_bucket_name` as outputs when the apply completes.

## Variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `aws_region` | `us-east-1` | no | AWS region |
| `instance_type` | `t3.small` | no | EC2 instance type |
| `key_pair_name` | — | **yes** | Existing EC2 key pair name |
| `bucket_name` | `fod-wpt-mlops-artifacts` | no | S3 bucket name |

Override defaults with `-var` flags or a `terraform.tfvars` file:

```hcl
# terraform.tfvars
aws_region    = "us-east-1"
instance_type = "t3.small"
key_pair_name = "my-key"
bucket_name   = "fod-wpt-mlops-artifacts"
```

## Tear down

```bash
terraform destroy -var="key_pair_name=<your-key-pair>"
```

> **Note:** The AWS resources described here are already provisioned. 
> These files serve as IaC documentation. Running `terraform apply` 
> against an existing account may conflict with manually created resources.
