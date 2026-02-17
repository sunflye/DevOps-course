provider "aws" {
  region = var.region
}

resource "aws_security_group" "vm_sg" {
  name        = "vm-sg"
  description = "Allow SSH, HTTP, 5000"
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Custom App"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "vm" {
  ami           = var.ami_id
  instance_type = var.instance_type
  security_groups = [aws_security_group.vm_sg.name]
  key_name = var.key_name
  tags = {
    Name = "devops-lab-vm"
  }
}

output "public_ip" {
  description = "Public IP"
  value = aws_instance.vm.public_ip
}