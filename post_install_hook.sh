# !/bin/bash

# This partially replicates pre_install_hook.sh with the reverse order of arguments
# and small adjustments
# (look in the comment there for the context)

info()
{
 cat << EOF

Usage: post_install_hook.sh --prefix=/opt/ --dep=openfoam4
or to use build caching with  ccache: post_install_hook.sh --dep=SU2 --ccache

EOF
}

PREFIX="$HOME"
DEP=""
CCACHE=false

for arg in "$@"
do
  case $arg in
    --prefix=*)
      PREFIX="${arg#*=}"
      shift
      ;;
    --dep*|--dependency=*)
      DEP="${arg#*=}"
      shift
      ;;
    -h|--help*)
      info
      exit 0
      ;;
      # sync ccache during compilation
      --ccache)
      CCACHE=true
      shift
      ;;
    *)
      printf "Unknown argument:  %s " "$arg"
      info
      exit 1
      ;;
  esac
done

if [ -z "$DEP" ]; then
  echo "Need to at least provide name of dependency to cache! "
  info
  exit 1
fi

# copy cache back to the individual folder and clean up the leftovers from previous builds
if [ "$CCACHE" = true ] && [ ! -z "$CCACHE_REMOTE" ]; then
        rsync -azpvrq --delete ${PREFIX}/.ccache/ ${CCACHE_REMOTE}/${DEP}
        exit 0
fi

# if we are on travis and this is the build with the first download, copy it back to the host
# let the remaining installation instructions in the docker file handle it, otherwise no need to do anything
if [ ! -z "${DEPS_REMOTE}" ] && [ !{ rsync --list-only "${DEPS_REMOTE}/${DEP}" > /dev/null 2>&1 } ]; then
  rsync -azpvrq ${PREFIX}/${DEP} ${DEPS_REMOTE}
fi
