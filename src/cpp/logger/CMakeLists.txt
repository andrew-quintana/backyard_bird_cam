# create a library for the logger module
add_library(logger
    logger.cpp
)

# link required libraries
find_package(nlohmann_json REQUIRED)
target_link_libraries(logger
    nlohmann_json::nlohmann_json
)

# specify include directories for the logger
target_include_directories(logger PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})