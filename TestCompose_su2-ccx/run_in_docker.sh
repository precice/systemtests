#! /bin/bash 

git clone https://github.com/precice/tutorials.git
sed -i -e 's|exchange-directory="../"|exchange-directory="/ExchangeDir/" network="eth0"|g' tutorials/FSI/flap_perp/SU2-CalculiX/precice-config-serial.xml
