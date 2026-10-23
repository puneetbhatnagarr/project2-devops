# S3 BUCKET (For storing uploaded Images)
resource "random_id" "bucket_suffix" {
  
  byte_length = 4
}

resource "aws_s3_bucket" "student_uploads" {
  bucket = "student-uploads-${random_id.bucket_suffix.hex}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "uploads_versioning" {
  bucket = aws_s3_bucket.student_uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 2. DYNAMODB (For storing the form data and "locking")

resource "aws_dynamodb_table" "student_data" {
  name = "StudentData"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "StudentID"

  attribute {
    name = "StudentID"
    type = "S"
  }
}

# 3. SNS (For sending the email notification)

resource "aws_sns_topic" "upload_alerts" { #tells Terraform to create an SNS Topic (a notification channel).
  name = "s3-upload-alerts" #is the actual name that will appear in the AWS Console
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.upload_alerts.arn
  protocol  = "email"
  endpoint  = "punitrock11@gmail.com" 
}

data "aws_iam_policy_document" "sns_policy" {
    # We used data "aws_iam_policy_document" because:

    #It's not creating anything real in AWS — it is just building a JSON text document.

    #It saves us from hand-typing JSON (which breaks easily).

  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"] #e are giving permission specifically to the S3 service.
    }
    actions   = ["SNS:Publish"] # We are allowing S3 to send messages (publish) to our SNS topic
    resources = [aws_sns_topic.upload_alerts.arn] # This permission applies to our specific SNS topic.
  }
}

# This attaches the policy we just wrote to the SNS topic. Now S3 is officially allowed to send messages to it.
resource "aws_sns_topic_policy" "default" {
    # amazon resource name
    # note for arn - arn:aws:SERVICE:REGION:ACCOUNT_ID:RESOURCE
    # arn:aws:sns:ap-south-1:123456789012:s3-upload-alerts
  arn = aws_sns_topic.upload_alerts.arn
  policy = data.aws_iam_policy_document.sns_policy.json
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.student_uploads.id
  topic {
    topic_arn = aws_sns_topic.upload_alerts.arn
    events    = ["s3:ObjectCreated:*"] #means "trigger this whenever a new file is created/uploaded".
  }
  depends_on = [aws_sns_topic_policy.default]
}

# 4. IAM ROLE (Giving EC2 permission to use S3 and DynamoDB)

resource "aws_iam_role" "ec2_role" { # Creates an IAM Role (an ID badge) named student-app-ec2-role.
  name = "student-app-ec2-role"
  assume_role_policy = jsonencode({ # assume_role_policy is a JSON document that defines who can wear this badge.
    Version = "2012-10-17"
    Statement = [{
          Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" } # Principal = { Service = "ec2.amazonaws.com" } means only EC2 servers are allowed to wear this badge.
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_full" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "dynamodb_full" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "student-app-ec2-profile"
  role = aws_iam_role.ec2_role.name
}