# Define the logger library
add_library(logger STATIC
    logger.cpp
)

# Link the logger library
target_include_directories(logger PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Build Python bindings for the logger
pybind11_add_module(logger_bindings logger_bindings.cpp)
target_link_libraries(logger_bindings PRIVATE logger)

# Set the output directory for the Python bindings
set_target_properties(logger_bindings PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/src/python
)