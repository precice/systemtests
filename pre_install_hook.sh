# !/bin/bash

# Contains series of operations, that should performed before installing
# dependenies. This includes caching of their source code to avoid
# failing builds due to network access on Travis (and corresponding
# waiting-for-download times ) as well as caching the c++ builds with
# ccache. Each dependency has individual folder for source
#  and ccache. Resultant hierarchy is the illustrated below:
#
# - cache
# -- ubuntu1604
# --- ccache
# ----- SU2
# ----- preCICE
# --- deps
# ----- SU2
# ----- preCICE

# It should be used before the chained command that does the compilation or fetches arhieves
# together with post_install_hook.sh right after the compilation command. In case of usage, please
# also pipe `return 0`, so that docker treats execution as successfull

info()
{
 cat << EOF

Usage: pre_install_hook.sh --prefix=/opt/ --dep=openfoam4
or to use build caching with  ccache: pre_install_hook.sh --dep=SU2 --ccache

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

# sync ccache if we are running on travis and actually want to sync
if [ "$CCACHE" = true ] && [ ! -z "$CCACHE_REMOTE" ]; then
        rsync -azpvrq ${CCACHE_REMOTE}/${DEP}/ ${PREFIX}/.ccache
        exit 0
fi

# if we are not on travis or folder with the corresponding version was not created yet,
# let the remaining installation instructions in the docker file handle it
if [ -z "${DEPS_REMOTE}" ] || [ rsync --list-only "${DEPS_REMOTE}/${DEP}" > /dev/null 2>&1 ]; then
  exit 0
# else just copy cached version and don't follow up with any chained commands
else
  rsync -azpvrq ${DEPS_REMOTE}/${DEP} ${PREFIX}
  exit 1
fi
