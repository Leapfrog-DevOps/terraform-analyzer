output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.main.id
}

output "public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.main.public_ip
}

output "private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.main.private_ip
}