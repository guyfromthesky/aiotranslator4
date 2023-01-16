pip3 install pyinstaller
pip3 install virtualenv
virtualenv ~/Documents/venv
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
cd ../
~/Documents/venv/bin/pip install -r requirements.txt