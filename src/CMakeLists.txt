cmake_minimum_required( VERSION 2.8 )

set(CMAKE_INSTALL_PREFIX /usr/local )

set(SRC_BASE_DIR ${CMAKE_CURRENT_SOURCE_DIR} )

set(CMAKE_INCLUDE_CURRENT_DIR ON )

# Globbing is not recommended -- CMake cannot tell when new files are added
# But for a generic skeleton...
file( GLOB_RECURSE 
    SRC_INCLUDE_FILES 
    ${SRC_BASE_DIR}/*.h
    ${SRC_BASE_DIR}/*.hpp
    )

file( GLOB_RECURSE 
    SRC_SOURCE_FILES
    ${SRC_BASE_DIR}/*.cpp
    ${SRC_BASE_DIR}/*.cc
    ${SRC_BASE_DIR}/*.C
    ${SRC_BASE_DIR}/*.mm
    )



set( ALL_SOURCES ${SRC_INCLUDE_FILES} ${SRC_SOURCE_FILES} )

add_executable( Experiment ${ALL_SOURCES})
target_include_directories(Experiment SYSTEM PUBLIC ../external/include)
target_link_libraries(Experiment GTest)

# INSTALL
# -------

install (
    TARGETS Experiment
    RUNTIME DESTINATION lib
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    )

