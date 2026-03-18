# ☁️ AWS Deployment Guide for ChessPulse

Complete guide to deploying ChessPulse on AWS using Elastic Beanstalk (backend) and S3/CloudFront (frontend).

## 📋 Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (`aws configure`)
- EB CLI installed (`pip install awsebcli`)
- Domain name (optional, for custom URL)

## 🔧 Setup AWS CLI

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Configure AWS credentials
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region (e.g., us-east-1)
# - Default output format (json)

# Verify installation
aws --version
```

## 🚀 Part 1: Deploy Backend to Elastic Beanstalk

### Step 1: Prepare Backend

```bash
cd backend

# Install EB CLI
pip install awsebcli

# Verify Dockerfile exists
ls -la Dockerfile
```

### Step 2: Initialize Elastic Beanstalk

```bash
# Initialize EB application
eb init -p docker chesspulse-api --region us-east-1

# Select or create new application
# Choose Docker platform
# Set up SSH (optional)
```

### Step 3: Create Environment and Deploy

```bash
# Create production environment
eb create chesspulse-prod --instance-type t2.small

# Wait for deployment (5-10 minutes)
# EB will build and deploy your Docker container

# Open in browser to test
eb open

# View logs if needed
eb logs
```

### Step 4: Configure Environment Variables (if needed)

```bash
# Set environment variables
eb setenv STOCKFISH_PATH=/usr/games/stockfish

# Or use the AWS Console:
# Elastic Beanstalk → Environments → Configuration → Software → Environment properties
```

### Step 5: Get Backend URL

```bash
# Get the public URL
eb status

# Example output will show:
# CNAME: chesspulse-prod.us-east-1.elasticbeanstalk.com
```

**Save this URL** - you'll need it for frontend configuration!

### Update Backend (After Changes)

```bash
# Deploy updated code
eb deploy

# View status
eb status

# View logs
eb logs --all
```

## 🌐 Part 2: Deploy Frontend to S3 + CloudFront

### Step 1: Create S3 Bucket

```bash
# Create bucket for frontend (must be globally unique)
aws s3 mb s3://chesspulse-demo-YOUR-UNIQUE-ID --region us-east-1

# Enable static website hosting
aws s3 website s3://chesspulse-demo-YOUR-UNIQUE-ID \
  --index-document index.html \
  --error-document index.html
```

### Step 2: Configure S3 Bucket Policy

Create a file `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::chesspulse-demo-YOUR-UNIQUE-ID/*"
    }
  ]
}
```

Apply the policy:

```bash
aws s3api put-bucket-policy \
  --bucket chesspulse-demo-YOUR-UNIQUE-ID \
  --policy file://bucket-policy.json
```

### Step 3: Build and Deploy Frontend

```bash
cd frontend

# Update .env with production backend URL
echo 'VITE_API=https://chesspulse-prod.us-east-1.elasticbeanstalk.com' > .env

# Build for production
npm run build

# Deploy to S3
aws s3 sync dist/ s3://chesspulse-demo-YOUR-UNIQUE-ID --delete

# Set proper content types
aws s3 cp dist/ s3://chesspulse-demo-YOUR-UNIQUE-ID \
  --recursive \
  --cache-control "max-age=3600" \
  --metadata-directive REPLACE
```

**Your site is now live!**  
URL: `http://chesspulse-demo-YOUR-UNIQUE-ID.s3-website-us-east-1.amazonaws.com`

### Step 4: Setup CloudFront CDN (Optional but Recommended)

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --origin-domain-name chesspulse-demo-YOUR-UNIQUE-ID.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html

# Get distribution ID from output
# Example: E1234567890ABC
```

Or use AWS Console:
1. Go to **CloudFront** → **Create Distribution**
2. **Origin domain**: Select your S3 bucket
3. **Viewer protocol policy**: Redirect HTTP to HTTPS
4. **Default root object**: `index.html`
5. **Create distribution**

Wait 10-15 minutes for deployment, then access via CloudFront URL.

### Step 5: Update Frontend After Changes

```bash
cd frontend

# Build latest changes
npm run build

# Deploy to S3
aws s3 sync dist/ s3://chesspulse-demo-YOUR-UNIQUE-ID --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

## 🔐 Part 3: Security & CORS Configuration

### Update Backend CORS (if using custom domain)

Edit `backend/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://your-cloudfront-domain.cloudfront.net",  # Production
        "https://yourdomain.com"  # Custom domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Deploy changes:
```bash
cd backend
eb deploy
```

## 💰 Cost Estimates (Monthly)

### Minimal Usage (Demo/Portfolio)
- **EC2 (t2.small)**: ~$17/month
- **S3 Storage (1GB)**: ~$0.03/month
- **CloudFront (10GB transfer)**: ~$1/month
- **Total**: ~$18/month

### Free Tier Eligible (First Year)
- EC2: 750 hours/month free (t2.micro)
- S3: 5GB storage free
- CloudFront: 50GB transfer free
- **Potential Total**: $0-5/month

## 🔄 CI/CD Pipeline (Optional)

### GitHub Actions Deployment

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy ChessPulse

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to EB
        run: |
          pip install awsebcli
          cd backend
          eb deploy chesspulse-prod
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and Deploy
        run: |
          cd frontend
          npm install
          npm run build
          aws s3 sync dist/ s3://chesspulse-demo-YOUR-UNIQUE-ID --delete
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 🧹 Cleanup (To Avoid Charges)

### Delete Backend

```bash
cd backend
eb terminate chesspulse-prod
```

### Delete Frontend

```bash
# Empty S3 bucket
aws s3 rm s3://chesspulse-demo-YOUR-UNIQUE-ID --recursive

# Delete bucket
aws s3 rb s3://chesspulse-demo-YOUR-UNIQUE-ID

# Delete CloudFront distribution (via Console)
# 1. Disable distribution
# 2. Wait for status to change
# 3. Delete distribution
```

## 🐛 Troubleshooting

### Backend Issues

**504 Gateway Timeout**
- Increase timeout in EB Console: Configuration → Software → Timeout (300 seconds)

**App not starting**
```bash
eb logs
# Check for Python/Docker errors
# Verify requirements.txt has all dependencies
```

**Stockfish not found**
- Update Dockerfile to install stockfish
- Or remove Stockfish dependency and use neural net only

### Frontend Issues

**API calls failing**
- Check CORS configuration in backend
- Verify backend URL in `.env` is correct
- Check browser console for errors

**404 errors on refresh**
- Add error document: `index.html` in S3 website config
- CloudFront: Add custom error response (404 → 200 → /index.html)

## 📊 Monitoring

### Backend Monitoring
```bash
# View environment health
eb health

# Stream logs in real-time
eb logs --stream
```

### AWS Console Monitoring
- **CloudWatch**: View logs and metrics
- **Elastic Beanstalk**: Environment health dashboard
- **S3**: Storage usage and requests
- **CloudFront**: Traffic and error rates

## 🎯 Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] API calls working end-to-end
- [ ] CloudFront HTTPS enabled
- [ ] Custom domain configured (optional)
- [ ] Monitoring/logging setup
- [ ] Cost alerts configured
- [ ] Backup strategy defined

---

## 📚 Additional Resources

- [AWS Elastic Beanstalk Docs](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Distribution Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/)

---

**Congratulations! Your ChessPulse app is now live! 🎉**

