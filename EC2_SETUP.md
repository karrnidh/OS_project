# AWS EC2 Setup Guide

This guide explains how to:

- Access an AWS EC2 instance  
- Upload project files  
- Run the scheduling simulator  
- Generate and download Gantt charts  
- Capture screenshots for the report  

---

# 1. Fix Permissions on `.pem` Key

### **Windows (PowerShell)**

``powershell
icacls keypair.pem /inheritance:r
icacls keypair.pem /grant:r "$($env:UserName):(R)"
Linux / macOS
chmod 400 keypair.pem
---
# 2. SSH into Your EC2 Instance
Amazon Linux
ssh -i "keypair.pem" ec2-user@<EC2-PUBLIC-IP>
Ubuntu
ssh -i "keypair.pem" ubuntu@<EC2-PUBLIC-IP>
---
# 3. Upload Python Files to EC2 (SCP)
From your local machine:
scp -i "keypair.pem" scheduling.py subnetting.py ec2-user@<EC2-PUBLIC-IP>:/home/ec2-user/
---
## Then inside EC2:
# 4. Install Python & Dependencies on EC2
sudo yum install python3 -y    # Amazon Linux
pip3 install pandas matplotlib
---
# 5. Run the Scheduling Simulator
python3 scheduling.py
This will:
Fetch live Linux processes
Run FCFS, SJF, Priority, RR
Generate comparison tables
Save Gantt charts as PNG files (EC2 is headless)

Check saved charts:
ls *.png
---
# 6. Download Gantt Charts Back to Your Laptop
From your local machine:
scp -i "keypair.pem" ec2-user@<EC2-PUBLIC-IP>:/home/ec2-user/*.png .
---
# 7. Run the Subnetting Tool
python3 subnetting.py
