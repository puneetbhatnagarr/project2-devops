variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}


# Change the ssh_allowed_cidr value below to YOUR public IP.
# Get your IP from: https://checkip.amazonaws.com
# Add /32 at the end.
variable "my_ip" {
  description = "Your public IP with /32"
  type        = string
  default     = "106.219.166.213/32"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "Ubuntu 22.04 AMI ID for ap-south-1"
  type        = string
  default     = "ami-01a00762f46d584a1"
}

variable "key_pair_name" {
  description = "Name of the EC2 key"
  type        = string
  default     = "devi"
}