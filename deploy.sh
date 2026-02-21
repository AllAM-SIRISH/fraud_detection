#!/bin/bash

# AWS EC2 Deployment Script
echo "Setting up Fraud Detection System on AWS EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r backend/requirements.txt

# Install nginx for frontend
sudo apt install nginx -y

# Copy frontend files to nginx
sudo cp -r frontend/* /var/www/html/

# Start the application
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &

echo "Deployment complete!"
echo "Backend: http://your-ec2-ip:8000"
echo "Frontend: http://your-ec2-ip"
