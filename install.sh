#!/bin/bash
sudo rm /usr/bin/manpac
sudo rm -rf /opt/manpac
sudo pacman -S python-virtualenv --noconfirm
virtualenv manpacqt
source /opt/manpac/manpacqt/bin/activate
pip3 --no-input install PyQt5 
deactivate
sudo cp -r ../manpac  /opt/manpac
rm -rf ../manpac
cd /opt/manpac
sudo chmod +x install.sh
sudo chmod +x manpac.sh
sudo ln -s /opt/manpac/manpac.sh /usr/bin/manpac
