# 1. Open and replace the file
sudo nano /home/ubuntu/app.py
# Copy content of app.py and paste it here, then save and exit

# 2. Make sure flask is installed
sudo apt-get update -y
sudo apt-get install -y python3-flask

# 3. Restart service
sudo systemctl daemon-reload
sudo systemctl restart sampleapp
sudo systemctl status sampleapp
