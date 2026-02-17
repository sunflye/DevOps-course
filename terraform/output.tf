output "ssh_command" {
  value       = "ssh ubuntu@${aws_instance.vm.public_ip}"
  description = "SSH command"
}