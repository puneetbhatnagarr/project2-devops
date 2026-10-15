output "public_ip" {
  value = aws_instance.k8s_node.public_ip
}

output "ssh_command" {
  value = "ssh -i verginia.pem ubuntu@${aws_instance.k8s_node.public_ip}"
}