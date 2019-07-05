#/bin/bash

ROOT_DIR=$(pwd)
#git clone https://github.com/precice/tutorials.git
#cd tutorials/FSI/flap_perp/SU2-CalculiX
#sed -i -e 's|exchange-directory="/.."|exchange-directory="/ExchangeDir/" network="eth0"|g' precice-config-serial.xml

 docker run -it --network=precice_comm --mount type=bind,source=${ROOT_DIR}/tutorials/FSI/flap_perp/SU2-CalculiX,target=/Input --mount source=exchange,target=/ExchangeDir --name calculix calculix-adapter /bin/bash -c "cd /Input/ ; ccx_preCICE -i flap -precice-participant Calculix"
# 
#docker run -it --network=precice_comm --mount type=bind,source=${ROOT_DIR}/tutorials/FSI/flap_perp/SU2-CalculiX,target=/Input --mount source=exchange,target=/ExchangeDir --name calculix calculix-adapter /bin/bash
