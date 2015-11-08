# Note, must specify 'CXX' as the project language, or CMAKE_<TYPE>_LIBRARY_SUFFIX/PREFIX will not be set
project(ISY_EXTERNALS CXX)

cmake_minimum_required(VERSION 3.1 FATAL_ERROR)
list(APPEND CMAKE_MODULE_PATH "../../cmake")
# Because we use 'make' as a build command, CMake will warn us that we may be expecting that
# to be expanded to a variable value.
cmake_policy(SET CMP0054 NEW)


find_program(BASH_PROGRAM bash)
if (UNIX AND NOT APPLE)
    message("BUBUBU")
    # For Ubuntu, the default is Clang 3.5, which does not use C++11 / libc++ by default.
    # So we generate a wrapper script to call clang with the appropriate flags
    set(CXX_STDLIB libc++)
    set(CMAKE_CXX_STANDARD 11)
    configure_file(compile-cxx.in compile-cxx)
    execute_process(COMMAND chmod ug+x compile-cxx)
    set(CMAKE_CXX_COMPILER ${CMAKE_CURRENT_SOURCE_DIR}/compile-cxx)
    set(ENV{CXX}  ${CMAKE_CURRENT_SOURCE_DIR}/compile-cxx)
endif()

set (ep_base ${CMAKE_CURRENT_SOURCE_DIR})

set_directory_properties(PROPERTIES 
    EP_BASE ${ep_base}
    )

set(patches_dir ${ep_base}/patches)
set_property(DIRECTORY PROPERTY "EP_BASE" ${ep_base})
set(external_source_base_dir ${ep_base}/Source)
set(external_build_base_dir ${ep_base}/Build)
set(external_install_base_dir ${ep_base}/Install)
set(ExternalIncludeDir ${CMAKE_CURRENT_SOURCE_DIR}/../include)
set(ExternalLibraryDir ${CMAKE_CURRENT_SOURCE_DIR}/../lib)

include(ExternalProject)
include(LibrarySuffixes)

set(LOG_EXTERNALS ON CACHE BOOL "Log external downloads, etc.")

find_program(PATCH patch)
if(PATCH-NOTFOUND)
    message(FATAL "Could not find patch program in path! If on windows, install Cygwin's patch")
else()
    message("Found patch command: ${PATCH}")
endif()


#                __                    _   
#  __ _ __ _ __ / _|___ _ _ _ __  __ _| |_ 
# / _| '_ \ '_ \  _/ _ \ '_| '  \/ _` |  _|
# \__| .__/ .__/_| \___/_| |_|_|_\__,_|\__|
#    |_|  |_|                              
# Install cppformat  
set(CPPFORMAT_USE_DYNAMIC OFF CACHE BOOL "Use dynamic lib format Library")

set_library_prefix_and_suffix(CPPFORMAT_USE_DYNAMIC CPPFORMAT_LIBRARY_PREFIX CPPFORMAT_LIBRARY_SUFFIX)

ExternalProject_Add(
    CppFormat
    GIT_REPOSITORY https://github.com/antmd/cppformat.git
    GIT_TAG build_options
    TIMEOUT 20
    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR> -DBUILD_TESTS:BOOL=NO -DBUILD_DOCS:BOOL=NO -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    UPDATE_COMMAND ""
    PATCH_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(CppFormat install_dir)
set(CPPFORMAT_INSTALL_DIR ${install_dir})
set(CPPFORMAT_INCLUDE_DIRS ${install_dir}/include CACHE INTERNAL "")
set(CPPFORMAT_LIBRARY ${CPPFORMAT_LIBRARY_PREFIX}format${CPPFORMAT_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(CPPFORMAT_LIBRARY_PATH ${install_dir}/lib/${CPPFORMAT_LIBRARY})

ExternalProject_Add_Step(CppFormat cppformat_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CPPFORMAT_INCLUDE_DIRS}" ${ExternalIncludeDir}/cppformat
    COMMAND ${CMAKE_COMMAND} -E copy "${CPPFORMAT_LIBRARY_PATH}" ${ExternalLibraryDir}
    )

#   ___               _    _                   
#  / __|__ _ ___ __ _| |__| |__ _ _ _  __ __ _ 
# | (__/ _` (_-</ _` | '_ \ / _` | ' \/ _/ _` |
#  \___\__,_/__/\__,_|_.__/_\__,_|_||_\__\__,_|
#                                              
# C++ REST SDK
set(CASABLANCA_SOURCE_DIR ${external_source_base_dir}/Casablanca)
set(CASABLANCA_USE_DYNAMIC OFF CACHE BOOL "Use C++ network library")

set_library_prefix_and_suffix(CASABLANCA_USE_DYNAMIC CASABLANCA_LIBRARY_PREFIX CASABLANCA_LIBRARY_SUFFIX)

ExternalProject_Add(
    Casablanca
    GIT_REPOSITORY https://github.com/antmd/casablanca.git
    GIT_TAG master
    TIMEOUT 20
    #BUILD_COMMAND ${ISY_SCRIPT_DIR}/build_casablanca.sh ${CASABLANCA_SOURCE_DIR}
    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR> -DBUILD_SHARED_LIBS=${CASABLANCA_USE_DYNAMIC} -DBUILD_TESTS=OFF -DBUILD_SAMPLES=OFF -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    PATCH_COMMAND ${PATCH} -p1 -f -N < ${patches_dir}/casablanca-xcode7.patch || true
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(Casablanca install_dir)
ExternalProject_Get_Property(Casablanca source_dir)
set(CASABLANCA_LIBRARY ${CASABLANCA_LIBRARY_PREFIX}cpprest${CASABLANCA_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(CASABLANCA_UTILITIES_LIBRARY ${CASABLANCA_LIBRARY_PREFIX}common_utilities${CASABLANCA_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(CASABLANCA_LIBRARY_PATH ${install_dir}/lib/${CASABLANCA_LIBRARY})
set(CASABLANCA_INCLUDE_DIRS ${install_dir}/include CACHE INTERNAL "")
set(WEBSOCKETPP_INCLUDE_DIRS ${source_dir}/Release/libs/websocketpp CACHE INTERNAL "")

ExternalProject_Add_Step(Casablanca casablanca_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy "${CASABLANCA_LIBRARY_PATH}" ${ExternalLibraryDir}
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CASABLANCA_INCLUDE_DIRS}" ${ExternalIncludeDir}
    # Copy embedded WebsocketPP
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${source_dir}/Release/libs/websocketpp/websocketpp" ${ExternalIncludeDir}/websocketpp
    )
if (CASABLANCA_USE_DYNAMIC)
    set(CASABLANCA_UTILITIES_LIBRARY_PATH ${CMAKE_CURRENT_SOURCE_DIR}/lib/${CASABLANCA_UTILITIES_LIBRARY})
    ExternalProject_Add_Step(Casablanca casablanca_install_utilities
        DEPENDEES install
        COMMAND ${CMAKE_COMMAND} -E copy "${CASABLANCA_UTILITIES_LIBRARY_PATH}" ${ExternalLibraryDir}
        )
endif()



#  _ _ _                   __ 
# | (_) |__  __ _ _____ __/ _|
# | | | '_ \/ _` / -_) \ /  _|
# |_|_|_.__/\__, \___/_\_\_|  
#           |___/             
# GEXF graph format
set(LIBGEXF_SOURCE_DIR ${external_source_base_dir}/LibGEXF)
set(LIBGEXF_USE_DYNAMIC OFF CACHE BOOL "Use dynamic libGEXF library")

find_package(LibXml2 REQUIRED)
set_library_prefix_and_suffix(LIBGEXF_USE_DYNAMIC LIBGEXF_LIBRARY_PREFIX LIBGEXF_LIBRARY_SUFFIX)

ExternalProject_Add(
    LibGEXF
    GIT_REPOSITORY https://github.com/antmd/libgexf.git
    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR> -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    TIMEOUT 20
    PATCH_COMMAND ""
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(LibGEXF install_dir)
set(LIBGEXF_INSTALL_DIR ${install_dir})
set(LIBGEXF_LIBRARY ${LIBGEXF_LIBRARY_PREFIX}gexf${LIBGEXF_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(LIBGEXF_LIBRARY_PATH ${install_dir}/lib/${LIBGEXF_LIBRARY} CACHE INTERNAL "")
set(LIBGEXF_INCLUDE_DIRS ${install_dir}/include CACHE INTERNAL "")

ExternalProject_Add_Step(LibGEXF libgexf_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${LIBGEXF_INCLUDE_DIRS}" ${ExternalIncludeDir}
    COMMAND ${CMAKE_COMMAND} -E copy "${LIBGEXF_LIBRARY_PATH}" ${ExternalLibraryDir}
    )

#
#  ___       ___           
# | _ \__ __/ __|_ __ _ __ 
# |   /\ \ / (__| '_ \ '_ \
# |_|_\/_\_\\___| .__/ .__/
#               |_|  |_|   
set(RXCPP_SOURCE_DIR ${external_source_base_dir}/RxCpp)

set_library_prefix_and_suffix(RXCPP_USE_DYNAMIC RXCPP_LIBRARY_PREFIX RXCPP_LIBRARY_SUFFIX)

include_directories(${external_source_base_dir}/TBB/mac/include)
ExternalProject_Add(
    RxCpp
    GIT_REPOSITORY https://github.com/Reactive-Extensions/RxCpp.git
    GIT_TAG 71254f2e6a51fe861869f22a1eaebd9d09001132
    TIMEOUT 20
    BUILD_COMMAND ""
    PATCH_COMMAND ""
    CONFIGURE_COMMAND ""
    INSTALL_COMMAND ""
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(RxCpp source_dir)
set(RXCPP_INSTALL_DIR ${source_dir})
set(RXCPP_INCLUDE_DIRS ${source_dir}/Rx/v2/src CACHE INTERNAL "")

ExternalProject_Add_Step(RxCpp rxcpp_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${source_dir}/Rx/v2/src" ${ExternalIncludeDir}
    )

#  ___ _               
# | __(_)__ _ ___ _ _  
# | _|| / _` / -_) ' \ 
# |___|_\__, \___|_||_|
#       |___/          
# Eigen matrix algebra -- headers-only
set(EIGEN_SOURCE_DIR ${external_source_base_dir}/eigen)

ExternalProject_Add(
    Eigen
    GIT_REPOSITORY https://github.com/RLovelett/eigen.git
    GIT_TAG 4084c8fe40d29fb12e786c6cfdbae1428ccf5e22
    CMAKE_ARGS -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR> -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    TIMEOUT 20
    PATCH_COMMAND ""
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(Eigen install_dir)
set(EIGEN_INSTALL_DIR ${install_dir})
set(EIGEN_INCLUDE_DIRS ${install_dir}/include/eigen3 CACHE INTERNAL "")

ExternalProject_Add_Step(Eigen eigen_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${EIGEN_INCLUDE_DIRS}/Eigen" ${ExternalIncludeDir}/Eigen
    )


#  ___              _      ___                   _              ___              _                        _   
# | _ ) ___  ___ __| |_   / __|___ ___ _ __  ___| |_ _ _ _  _  |   \ _____ _____| |___ _ __ _ __  ___ _ _| |_ 
# | _ \/ _ \/ _ (_-<  _| | (_ / -_) _ \ '  \/ -_)  _| '_| || | | |) / -_) V / -_) / _ \ '_ \ '  \/ -_) ' \  _|
# |___/\___/\___/__/\__|  \___\___\___/_|_|_\___|\__|_|  \_, | |___/\___|\_/\___|_\___/ .__/_|_|_\___|_||_\__|
#                                                        |__/                         |_|                     
# Boost Geometry, development branch -- disabled

#[[
ExternalProject_Add(
    BoostGeometry
    GIT_REPOSITORY https://github.com/boostorg/geometry.git
    GIT_TAG "develop"
    TIMEOUT 20
    BUILD_COMMAND ""
    CONFIGURE_COMMAND ""
    PATCH_COMMAND ""
    INSTALL_COMMAND ""
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(BoostGeometry source_dir)
set(BOOST_GEOMETRY_SOURCE_DIR ${source_dir})
set(BOOST_GEOMETRY_INSTALL_DIR ${source_dir})
set(BOOST_GEOMETRY_INCLUDE_DIRS ${source_dir}/include CACHE INTERNAL "")

ExternalProject_Add_Step(BoostGeometry boostgeometry_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${BOOST_GEOMETRY_INCLUDE_DIRS}" ${ExternalIncludeDir}
    )
]]


#  ___              _     ___                       
# | _ ) ___  ___ __| |_  | _ \_ _ ___  __ ___ ______
# | _ \/ _ \/ _ (_-<  _| |  _/ '_/ _ \/ _/ -_|_-<_-<
# |___/\___/\___/__/\__| |_| |_| \___/\__\___/__/__/
#                                                   
# Boost Process, boost incubator project

ExternalProject_Add(
    BoostProcess
    GIT_REPOSITORY https://github.com/BorisSchaeling/boost-process.git
    GIT_TAG 43dc0082339346dd4242289f5b2ccb026506361e
    TIMEOUT 20
    BUILD_COMMAND ""
    CONFIGURE_COMMAND ""
    PATCH_COMMAND ""
    INSTALL_COMMAND ""
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(BoostProcess source_dir)
set(BOOST_PROCESS_SOURCE_DIR ${source_dir})
set(BOOST_PROCESS_INSTALL_DIR ${source_dir})
set(BOOST_PROCESS_INCLUDE_DIRS ${source_dir}/boost CACHE INTERNAL "")

ExternalProject_Add_Step(BoostProcess boostprocess_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${BOOST_PROCESS_INCLUDE_DIRS}" ${ExternalIncludeDir}/boost
    )


#     _              
#    (_)___ ___ _ _  
#    | (_-</ _ \ ' \ 
#   _/ /__/\___/_||_|
#  |__/              
# Modern JSON library
set(JSON_SOURCE_DIR ${external_source_base_dir}/json)

ExternalProject_Add(
    Json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG 4c55ada0f7a90a802cb443385e34f26021ff83db
    TIMEOUT 20
    CONFIGURE_COMMAND ""
    INSTALL_COMMAND "" 
    PATCH_COMMAND ""
    BUILD_COMMAND ""
    BUILD_IN_SOURCE 1
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(Json source_dir)
set(JSON_INCLUDE_DIRS ${source_dir}/src CACHE INTERNAL "")

ExternalProject_Add_Step(Json json_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy "${JSON_INCLUDE_DIRS}/json.hpp" ${ExternalIncludeDir}/json/json.hpp
    )

#            _                     _   _ _   _          
#  _ __  ___| |_  _ _ __  __ _ _ _| |_(_) |_(_)___ _ _  
# | '_ \/ _ \ | || | '_ \/ _` | '_|  _| |  _| / _ \ ' \ 
# | .__/\___/_|\_, | .__/\__,_|_|  \__|_|\__|_\___/_||_|
# |_|          |__/|_|                                  
# Tiny Triangulation library 
set(POLYPARTITION_SOURCE_DIR ${external_source_base_dir}/polypartition)

ExternalProject_Add(
    PolyPartition
    GIT_REPOSITORY https://github.com/ivanfratric/polypartition.git
    GIT_TAG 585f34a9f751a57a0191a42750cca7afd148afdb
    TIMEOUT 20
    CONFIGURE_COMMAND ""
    INSTALL_COMMAND "" 
    PATCH_COMMAND ""
    UPDATE_COMMAND ""
    BUILD_COMMAND ${CMAKE_CXX_COMPILER} -c <SOURCE_DIR>/src/polypartition.cpp
    BUILD_IN_SOURCE 1
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(PolyPartition source_dir)
set(POLYPARTITION_ ${source_dir})
set(POLYPARTITION_LIBRARY polypartition.o CACHE INTERNAL "")
set(POLYPARTITION_LIBRARY_PATH ${source_dir}/${POLYPARTITION_LIBRARY})
set(POLYPARTITION_INCLUDE_DIRS ${source_dir}/src CACHE INTERNAL "")

ExternalProject_Add_Step(PolyPartition polypartition_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy "${POLYPARTITION_INCLUDE_DIRS}/polypartition.h" ${ExternalIncludeDir}/polypartition/polypartition.h
    COMMAND ${CMAKE_COMMAND} -E copy "${POLYPARTITION_LIBRARY_PATH}" ${ExternalLibraryDir}
    )

#   ___ ___ _              
#  / __| __| |__ _ __ _ ___
# | (_ | _|| / _` / _` (_-<
#  \___|_| |_\__,_\__, /__/
#                 |___/    
# Install GFlags
# Note, need to used 'google' namespace for compatibility with glog
set(GFLAGS_SOURCE_DIR ${external_source_base_dir}/GFlags)
set(GFLAGS_USE_DYNAMIC OFF CACHE BOOL "Use dynamic Google Flags Library")

set_library_prefix_and_suffix(GFLAGS_USE_DYNAMIC GFLAGS_LIBRARY_PREFIX GFLAGS_LIBRARY_SUFFIX)

ExternalProject_Add(
    GFlags
    GIT_REPOSITORY https://code.google.com/p/gflags/
    GIT_TAG 05b155ff59114735ec8cd089f669c4c3d8f59029
    TIMEOUT 20
    CMAKE_ARGS -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR> -DGFLAGS_NAMESPACE=google -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    PATCH_COMMAND ${PATCH} -p1 -f -N < ${patches_dir}/gflags-vs2015.patch || true
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
    )

ExternalProject_Get_Property(GFlags install_dir)
set(GFLAGS_INSTALL_DIR ${install_dir})
set(GFLAGS_LIBRARY ${GFLAGS_LIBRARY_PREFIX}gflags${GFLAGS_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(GFLAGS_LIBRARY_PATH ${install_dir}/lib/${GFLAGS_LIBRARY})
set(GFLAGS_INCLUDE_DIRS ${install_dir}/include CACHE INTERNAL "")

ExternalProject_Add_Step(GFlags gflags_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${install_dir}/include/gflags" ${ExternalIncludeDir}/gflags
    COMMAND ${CMAKE_COMMAND} -E copy "${GFLAGS_LIBRARY_PATH}" ${ExternalLibraryDir}
    )

#   ___ _              
#  / __| |   ___  __ _ 
# | (_ | |__/ _ \/ _` |
#  \___|____\___/\__, |
#                |___/ 
# Install GLog
set(GLOG_SOURCE_DIR ${external_source_base_dir}/GLog)
set(GLOG_USE_DYNAMIC OFF CACHE BOOL "Use dynamic Google Logging Library")

set_library_prefix_and_suffix(GLOG_USE_DYNAMIC GLOG_LIBRARY_PREFIX GLOG_LIBRARY_SUFFIX)

if (WIN32)
    ExternalProject_Add(
        GLog
        GIT_REPOSITORY https://github.com/google/glog.git
        GIT_TAG  1b0b08c8dda1659027677966b03a3ff3c488e549
        TIMEOUT 20
        CONFIGURE_COMMAND ""
        BUILD_COMMAND ${ISY_SCRIPT_DIR}/msbuild-wrapper.bat ${GLOG_SOURCE_DIR}/google-glog.sln
        INSTALL_COMMAND ""
        UPDATE_COMMAND ""
        LOG_DOWNLOAD "${LOG_EXTERNALS}"
        LOG_UPDATE "${LOG_EXTERNALS}"
        LOG_CONFIGURE "${LOG_EXTERNALS}"
        LOG_BUILD "${LOG_EXTERNALS}"
        DEPENDS GFlags
        )
else()
    ExternalProject_Add(
        GLog
        GIT_REPOSITORY https://github.com/google/glog.git
        GIT_TAG  1b0b08c8dda1659027677966b03a3ff3c488e549
        TIMEOUT 20
        CONFIGURE_COMMAND ${BASH_PROGRAM} -c "CXX=${CMAKE_CXX_COMPILER} <SOURCE_DIR>/configure --prefix=<INSTALL_DIR>  --with-gflags=${GFLAGS_INSTALL_DIR} --disable-shared"
        BUILD_COMMAND "make"
        INSTALL_COMMAND "make" "install"
        UPDATE_COMMAND ""
        LOG_DOWNLOAD ${LOG_EXTERNALS}
        LOG_UPDATE ${LOG_EXTERNALS}
        LOG_CONFIGURE ${LOG_EXTERNALS}
        LOG_BUILD ${LOG_EXTERNALS}
        LOG_INSTALL ${LOG_EXTERNALS}
        )
endif()

add_dependencies(GLog GFlags)

# GLog isn't CMake compatible, so we build 'in source', and then pick out relevant directories
ExternalProject_Get_Property(GLog source_dir)
ExternalProject_Get_Property(GLog install_dir)
set(GLOG_LIBRARY ${GLOG_LIBRARY_PREFIX}glog${GLOG_LIBRARY_SUFFIX} CACHE INTERNAL "")
if (WIN32)
    set(GLOG_INCLUDE_DIRS ${source_dir}/src/windows CACHE INTERNAL "")
    set(GLOG_LIBRARY_PATH ${source_dir}/$<CONFIG>/${GLOG_LIBRARY})
else()
    set(GLOG_INCLUDE_DIRS ${install_dir}/include CACHE INTERNAL "")
    set(GLOG_LIBRARY_PATH ${install_dir}/lib/${GLOG_LIBRARY} CACHE INTERNAL "")
endif()

ExternalProject_Add_Step(GLog glog_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${GLOG_INCLUDE_DIRS}" ${ExternalIncludeDir}
    COMMAND ${CMAKE_COMMAND} -E copy "${GLOG_LIBRARY_PATH}" ${ExternalLibraryDir}
    )

#   ___ __  __         _       _      ___ _____       _   
#  / __|  \/  |___  __| |__  _| |_   / __|_   _|__ __| |_ 
# | (_ | |\/| / _ \/ _| / / |_   _| | (_ | | |/ -_|_-<  _|
#  \___|_|  |_\___/\__|_\_\   |_|    \___| |_|\___/__/\__|
#                                                         
# Add gmock
ExternalProject_Add(
    GMock
    SVN_REPOSITORY http://googlemock.googlecode.com/svn/trunk
    SVN_REVISION -r507
    TIMEOUT 20
    # Force separate output paths for debug and release builds to allow easy
    # identification of correct lib in subsequent TARGET_LINK_LIBRARIES commands
    #CMAKE_ARGS -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_DEBUG:PATH=DebugLibs -DCMAKE_ARCHIVE_OUTPUT_DIRECTORY_RELEASE:PATH=ReleaseLibs -Dgtest_force_shared_crt=ON
    CMAKE_ARGS -Dgtest_force_shared_crt=ON  -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
    # GMock has not install step in CMakeLists.txt
    INSTALL_COMMAND ""
    UPDATE_COMMAND ""
    LOG_DOWNLOAD ${LOG_EXTERNALS}
    LOG_UPDATE ${LOG_EXTERNALS}
    LOG_CONFIGURE ${LOG_EXTERNALS}
    LOG_BUILD ${LOG_EXTERNALS}
    LOG_INSTALL ${LOG_EXTERNALS}
)



# GMock isn't installed, but it does is CMake compatible, so we need to get stuff from the build directory 'BINARY_DIR'
ExternalProject_Get_Property(GMock binary_dir)
ExternalProject_Get_Property(GMock source_dir)
set(GTEST_USE_DYNAMIC OFF CACHE BOOL "Use dynamic Google Test Library")
set_library_prefix_and_suffix(GTEST_USE_DYNAMIC GTEST_LIBRARY_PREFIX GTEST_LIBRARY_SUFFIX)

if (IS_SINGLE_CONFIG_GENERATOR)
    set(gmock_config_dir .)
else()
    set(gmock_config_dir $<CONFIG>)
endif()

set(GMOCK_INCLUDE_DIRS ${source_dir}/include CACHE INTERNAL "")
set(GMOCK_LIBRARY ${GTEST_LIBRARY_PREFIX}gmock${GTEST_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(GMOCK_LIBRARY_PATH ${binary_dir}/${gmock_config_dir}/${GMOCK_LIBRARY})
set(GMOCK_MAIN_LIBRARY ${GTEST_LIBRARY_PREFIX}gmock_main${GTEST_LIBRARY_SUFFIX})
set(GMOCK_MAIN_LIBRARY_PATH ${binary_dir}/${gmock_config_dir}/${GMOCK_MAIN_LIBRARY})


set(GTEST_INCLUDE_DIRS ${source_dir}/gtest/include CACHE INTERNAL "")
set(GTEST_LIBRARY ${GTEST_LIBRARY_PREFIX}gtest${GTEST_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(GTEST_LIBRARY_PATH ${binary_dir}/gtest/${gmock_config_dir}/${GTEST_LIBRARY})
set(GTEST_MAIN_LIBRARY ${GTEST_LIBRARY_PREFIX}gtest_main${GTEST_LIBRARY_SUFFIX} CACHE INTERNAL "")
set(GTEST_MAIN_LIBRARY_PATH ${binary_dir}/gtest/${gmock_config_dir}/${GTEST_MAIN_LIBRARY})

ExternalProject_Add_Step(GMock gmock_install
    DEPENDEES install
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${GMOCK_INCLUDE_DIRS}" ${ExternalIncludeDir}
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${GTEST_INCLUDE_DIRS}" ${ExternalIncludeDir}
    COMMAND ${CMAKE_COMMAND} -E copy "${GMOCK_LIBRARY_PATH}" ${ExternalLibraryDir}
    COMMAND ${CMAKE_COMMAND} -E copy "${GMOCK_MAIN_LIBRARY_PATH}" ${ExternalLibraryDir}
    COMMAND ${CMAKE_COMMAND} -E copy "${GTEST_LIBRARY_PATH}" ${ExternalLibraryDir}
    COMMAND ${CMAKE_COMMAND} -E copy "${GTEST_MAIN_LIBRARY_PATH}" ${ExternalLibraryDir}
    )

add_custom_target(AllExternals ALL)
add_dependencies(AllExternals 
    CppFormat
    Casablanca
    LibGEXF
    RxCpp
    Eigen
    #BoostGeometry
    BoostProcess
    Json
    PolyPartition
    GFlags
    GLog
    GMock
    )

