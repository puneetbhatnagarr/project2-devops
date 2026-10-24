output "public_ip" {
  value = aws_instance.k8s_node.public_ip
}

output "ssh_command" {
  value = "ssh -i devi.pem ubuntu@${aws_instance.k8s_node.public_ip}"
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.student_uploads.id
}

