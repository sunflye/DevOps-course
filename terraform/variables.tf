variable "region" {
  description = "AWS region for the VM"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "ami_id" {
  description = "AMI ID for Ubuntu 24.04 in us-east-1"
  default     = "ami-0b6c6ebed2801a5cb"
}


variable "key_name" {
  description = "Name of your uploaded EC2 keypair"
  default     = "vockey"
}