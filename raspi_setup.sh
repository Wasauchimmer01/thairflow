# User, Device name and Password are always identical


# 1. Install Git
# sudo apt install git -y

# 2. Make new folder and clone repo
# git clone https://inf-git.th-rosenheim.de/studsommal3080/airflow.git

# 3. Run setup
# cd airflow
# chmod +x raspi_setup.sh
# ./raspi_setup.sh
# source .venv/bin/activate


# Automatic parts of setup:
# 1. Update system
# sudo apt update && sudo apt upgrade -y
# 2. Check Pyhton
# python3 --version
# sould be 3.11.2
# 3. Check Pip
# pip --version
# sudo apt install python3 python3-pip -y



set -e

echo "🔄 Updating system..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Checking Python version..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found $PYTHON_VERSION"
else
    echo "❌ Python3 not found, installing..."
    sudo apt install python3 -y
fi

echo "📦 Checking pip version..."
if ! command -v pip3 &>/dev/null; then
    echo "❌ pip not found, installing..."
    sudo apt install python3-pip -y
else
    pip3 --version
fi

echo "📡 Enabling I2C interface..."

# Enable I2C in /boot/config.txt
sudo sed -i '/^#*dtparam=i2c_arm=/c\dtparam=i2c_arm=on' /boot/config.txt

# Load i2c-dev kernel module immediately
sudo modprobe i2c-dev

# Ensure module loads on every boot
echo "i2c-dev" | sudo tee -a /etc/modules

# Optional: install i2c-tools for testing
sudo apt install -y i2c-tools

echo "✅ I2C enabled."

echo "Installing gpio driver..."
sudo apt install -y python3-lgpio

echo "🐍 Setting up virtual environment..."
cd ~/airflow/airflow
python3 -m venv .venv

echo "✅ Setup complete! Reboot nessesary!!!."

echo "Scanning for I2C devices..."
i2cdetect -y 1