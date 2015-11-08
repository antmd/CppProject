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

ScriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )"
cd "$ScriptDir"

cmake -G'Unix Makefiles' && make -j8 AllExternals
