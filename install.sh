#!/bin/bash
sudo rm /usr/bin/manpac
virtualenv manpacqt
source /opt/manpac/manpacqt/bin/activate
pip3 --no-input install PyQt5 
deactivate
sudo cp -r ../manpac  /opt/manpac
rm -rf ../manpac
sudo pacman -S python-virtualenv --noconfirm
cd /opt/manpac
sudo ln -s /opt/manpac/manpac.sh /usr/bin/manpac