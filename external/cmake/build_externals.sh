#!/bin/bash - 
#===============================================================================
#
#          FILE: build_externals.sh
# 
#   DESCRIPTION: Build external dependencies of ISY Core
# 
#       CREATED: 2015-04-20
#
#        AUTHOR: Anthony Dervish
#
#===============================================================================

set -o nounset                              # Treat unset variables as an error

# Get the directory this script lives in, accounting for symlinks to the script
if [ -L "$0" ]; then
  pushd "$(dirname $0)/$(dirname $(readlink "$0"))" >/dev/null
else
  pushd $(dirname "$0") >/dev/null
fi
readonly ScriptDir=$(pwd)
popd >/dev/null


cd "$ScriptDir"


cd cmake
cmake -G'Unix Makefiles' && make -j8 AllExternals
