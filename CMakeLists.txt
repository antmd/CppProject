cmake_minimum_required( VERSION 3.0 )

set( CMAKE_INSTALL_PREFIX /usr/local )
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set(PROJECT_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR})

# Disallow in-tree build 
if( CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR )
  message(FATAL_ERROR "In-source builds are not allowed.
Please change to the 'build' directory and run cmake from there.
This process created the file `CMakeCache.txt' and the directory `CMakeFiles'.
Please delete them.")
endif()


project(CPPPROJECT)
include(CheckCXXCompilerFlag)

add_subdirectory(external)

check_cxx_compiler_flag("-std=c++11" SUPPORTS_CXX11)
if( SUPPORTS_CXX11 )
    set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
else()
    check_cxx_compiler_flag("-std=c++0x" SUPPORTS_CXX0X)
    if( SUPPORTS_CXX0X )
        set( CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
    else()
        message("C++11 is not supported")
    endif()
endif()


set(CPPPROJECT_BASE_DIR ${CMAKE_CURRENT_SOURCE_DIR} )

add_subdirectory(src)

