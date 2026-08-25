cmake_minimum_required(VERSION 3.20)
project(spotvol LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(spotvol_warnings INTERFACE)
if(MSVC)
    target_compile_options(spotvol_warnings INTERFACE /W4 /permissive-)
else()
    target_compile_options(spotvol_warnings INTERFACE -Wall -Wextra -Wpedantic)
endif()

file(GLOB SPOTVOL_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")

add_library(spotvol ${SPOTVOL_SOURCES})
target_include_directories(spotvol PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")
target_link_libraries(spotvol PRIVATE spotvol_warnings)

include(FetchContent)
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.15.2
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()
include(GoogleTest)

file(GLOB TEST_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.cpp")

foreach(source ${TEST_SOURCES})
    get_filename_component(target ${source} NAME_WE)
    add_executable(${target} ${source})
    target_link_libraries(${target} PRIVATE spotvol spotvol_warnings GTest::gmock_main)
    gtest_discover_tests(${target})
endforeach()
