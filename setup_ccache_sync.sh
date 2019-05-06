#!/bin/bash

# Starts rsync daemon that allows synchronization of ccache
# between host and docker container during image build stage
# use for speeding up build on CI machine

# folder for this particular build
PROJ_FOLDER=$1
if [  "$#" -lt 1 ]; then
  echo "Need to pass name of the folder where to store ccache for this build"
  exit 1
fi

# create folder in case they are not cached yet
mkdir -p $HOME/ccache
mkdir -p "$HOME/ccache/${PROJ_FOLDER}"

RSYNC_SERVER_IP=$( ip -4 -o addr show docker0 | awk '{print $4}' | cut -d "/" -f 1 )
RSYNC_CONFIG=$(mktemp)
# allow access from docker container
cat <<EOF > "${RSYNC_CONFIG}"
[precice-docker-cache]
        path = $HOME/ccache/${PROJ_FOLDER}
        comment = preCICE docker image cache
        hosts allow = 172.17.0.2
        use chroot = false
        read only = false
EOF
RSYNC_PORT=2342

# start rsync in deamon mode
rsync --port=${RSYNC_PORT} --address="${RSYNC_SERVER_IP}" --config="${RSYNC_CONFIG}" --daemon --no-detach &

CCACHE_REMOTE="rsync://${RSYNC_SERVER_IP}:${RSYNC_PORT}/precice-docker-cache"
