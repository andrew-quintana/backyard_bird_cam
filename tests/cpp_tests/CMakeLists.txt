# create an executable for the logger test
add_executable(test_logger
    test_logger.cpp
)

# link the logger library, gtest, and necessary dependencies
find_package(GTest REQUIRED)
target_link_libraries(test_logger
    logger
    GTest::GTest
    GTest::Main
    pthread
    nlohmann_json::nlohmann_json
)

# add the test to ctest
add_test(NAME LoggerTest COMMAND test_logger)