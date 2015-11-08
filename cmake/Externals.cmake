# Note, must specify 'CXX' as the project language, or CMAKE_<TYPE>_LIBRARY_SUFFIX/PREFIX will not be set
project(TravelPlanner_Externals CXX)

cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
list(APPEND CMAKE_MODULE_PATH "../cmake")
# Because we use 'make' as a build command, CMake will warn us that we may be expecting that
# to be expanded to a variable value.
cmake_policy(SET CMP0054 NEW)


find_program(BASH_PROGRAM bash)
if (UNIX AND NOT APPLE)
    # For Ubuntu, the default is Clang 3.5, which does not use C++11 / libc++ by default.
    # So we generate a wrapper script to call clang with the appropriate flags
    set(CXX_STDLIB libc++)
    set(CMAKE_CXX_STANDARD 11)
    configure_file(compile-cxx.in compile-cxx)
    execute_process(COMMAND chmod ug+x compile-cxx)
    set(CMAKE_CXX_COMPILER ${CMAKE_CURRENT_SOURCE_DIR}/compile-cxx)
    set(ENV{CXX}  ${CMAKE_CURRENT_SOURCE_DIR}/compile-cxx)
endif()

set (EpPrefix ${CMAKE_CURRENT_SOURCE_DIR}/externals)

set_directory_properties(PROPERTIES 
    EP_PREFIX ${EpPrefix}
    )

set(patches_dir ${EpPrefix}/patches)
set_property(DIRECTORY PROPERTY "EP_PREFIX" ${EpPrefix})
set(external_source_base_dir ${EpPrefix}/Source)
set(external_build_base_dir ${EpPrefix}/Build)
set(external_install_base_dir ${EpPrefix}/Install)
set(ExternalIncludeDir ${CMAKE_CURRENT_SOURCE_DIR}/include)
set(ExternalLibraryDir ${CMAKE_CURRENT_SOURCE_DIR}/lib)

include(ExternalProject)
include(LibrarySuffixes)

set(LOG_EXTERNALS ON CACHE BOOL "Log external downloads, etc.")

find_program(PATCH patch)
if(PATCH-NOTFOUND)
    message(FATAL "Could not find patch program in path! If on windows, install Cygwin's patch")
else()
    message("Found patch command: ${PATCH}")
endif()

set(all_externals "")

macro(GitHub _name _repo) # Optional: _tag
    if (${ARGC} GREATER 2)
        set(TAG_ARG "GIT_TAG ${ARG3}")
    endif()

    ExternalProject_Add(
        ${_name}
        GIT_REPOSITORY https://github.com/${_repo}.git
        ${TAG_ARG}
        TIMEOUT 20
        BUILD_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/make_external "${_name}" <SOURCE_DIR> <BINARY_DIR> <INSTALL_DIR>
        CONFIGURE_COMMAND ""
        UPDATE_COMMAND ""
        INSTALL_COMMAND ""
        PATCH_COMMAND ""
        LOG_DOWNLOAD ${LOG_EXTERNALS}
        LOG_UPDATE ${LOG_EXTERNALS}
        LOG_CONFIGURE ${LOG_EXTERNALS}
        LOG_BUILD ${LOG_EXTERNALS}
        LOG_INSTALL ${LOG_EXTERNALS}
        )
    list(APPEND all_externals ${_name})
endmacro()

macro(ZipFile _name _url)
    ExternalProject_Add(
        ${_name}
        URL ${_url}
        TIMEOUT 20
        BUILD_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/make_external "${_name}" <SOURCE_DIR> <BINARY_DIR> <INSTALL_DIR>
        CONFIGURE_COMMAND ""
        UPDATE_COMMAND ""
        INSTALL_COMMAND ""
        PATCH_COMMAND ""
        LOG_DOWNLOAD ${LOG_EXTERNALS}
        LOG_UPDATE ${LOG_EXTERNALS}
        LOG_CONFIGURE ${LOG_EXTERNALS}
        LOG_BUILD ${LOG_EXTERNALS}
        LOG_INSTALL ${LOG_EXTERNALS}
        )
    list(APPEND all_externals ${_name})
endmacro()

macro(Download _name _url _dest)
    string(CONCAT _target ${_name} "_external")
    add_custom_target(${_target}
        COMMAND
            message("Downloading ${_name} from ${_url} to ${_dest}")
            file(DOWNLOAD ${_url} ${CMAKE_CURRENT_SOURCE_DIR}/${_dest})
            )
    list(APPEND all_externals ${_target})
endmacro()

add_custom_target(AllExternals ALL)

if (EXISTS ${PROJECT_ROOT_DIR})
    include(${PROJECT_ROOT_DIR}/externals.txt)
    add_dependencies(AllExternals ${all_externals})
endif()

