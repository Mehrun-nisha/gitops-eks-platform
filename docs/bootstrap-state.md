# Bootstrapping remote Terraform state

Terraform state should not live on a laptop. Create an S3 bucket (versioned, encrypted)
and a DynamoDB table for state locking once, by hand or with a tiny separate stack:

```bash
REGION=ap-south-1
BUCKET=<your-unique-tfstate-bucket>

aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" \
  --create-bucket-configuration LocationConstraint="$REGION"
aws s3api put-bucket-versioning --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket "$BUCKET" \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws s3api put-public-access-block --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

aws dynamodb create-table --table-name terraform-locks --region "$REGION" \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

Then uncomment the `backend "s3"` block in `terraform/versions.tf` and run:

```bash
terraform init -migrate-state
```

**Why the lock table?** Two people (or two CI jobs) running `terraform apply` at the same
time would corrupt state. DynamoDB gives Terraform a lock so only one run proceeds.
