#!/bin/bash

# Starts rsync daemon that allows synchronization of files
# between host and docker container during image build stage
# use for speeding up build on CI machine, by caching C++ builds
# with ccache and source code of solvers

VARIANT_FOLDER=$1
if [  "$#" -lt 1 ]; then
  echo "Need to pass name of the folder where to store cache for the image variant"
  exit 1
fi

# create folders in case they are not cached yet
mkdir -p "$HOME/cache/${VARIANT_FOLDER}/ccache"
mkdir -p "$HOME/cache/${VARIANT_FOLDER}/dependencies"

RSYNC_SERVER_IP=$( ip -4 -o addr show docker0 | awk '{print $4}' | cut -d "/" -f 1 )
RSYNC_CONFIG=$(mktemp)
# allow access from docker container (we create only one, so name is hardcoded)
cat <<EOF > "${RSYNC_CONFIG}"
[build-ccache]
        path = $HOME/cache/${VARIANT_FOLDER}/ccache
        comment = preCICE docker image cache
        hosts allow = 172.17.0.2
        use chroot = false
        read only = false
[dependencies-source-cache]
        path = $HOME/cache/${VARIANT_FOLDER}/dependencies
        comment = cache of source code of solvers
        hosts allow = 172.17.0.2
        use chroot = false
        read only = false

EOF

RSYNC_PORT=2342

# start rsync in deamon mode
rsync --port=${RSYNC_PORT} --address="${RSYNC_SERVER_IP}" --config="${RSYNC_CONFIG}" --daemon --no-detach &

CCACHE_REMOTE="rsync://${RSYNC_SERVER_IP}:${RSYNC_PORT}/build-ccache"
DEPS_REMOTE="rsync://${RSYNC_SERVER_IP}:${RSYNC_PORT}/dependencies-source-cache"
