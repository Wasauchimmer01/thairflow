# User, Device name and Password are always identical


# 1. Install Git
# sudo apt install git -y

# 2. Make new folder and clone repo
# mkdir airflow
# cd airflow
# git clone https://inf-git.th-rosenheim.de/studsommal3080/airflow.git

# 3. Run setup
# chmod +x raspi_setup.sh
# ./raspi_setup.sh



# 1. Update system
# sudo apt update && sudo apt upgrade -y
# 3. Check Pyhton
# python3 --version
# sould be 3.11.2
# 4. Check Pip
# pip --version
# sudo apt install python3 python3-pip -y
# 5. Make new folder and clone repo
# mkdir airflow
# cd airflow
# git clone https://inf-git.th-rosenheim.de/studsommal3080/airflow.git



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

echo "✅ Setup complete!"