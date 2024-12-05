#include "logger.hpp"
#include <gtest/gtest.h>
#include <fstream>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

// helper function to read the last log entry
json getLastLogEntry(const std::string& logFilePath) {
    std::ifstream logFile(logFilePath, std::ios::in);
    std::string lastLine;
    std::string currentLine;

    while (std::getline(logFile, currentLine)) {
        lastLine = currentLine;
    }
    logFile.close();

    return json::parse(lastLine);
}

// test cases for logger
TEST(LoggerTest, LogsInfoMessage) {
    Logger::log("INFO", "cpp", "Test info message");

    auto logEntry = getLastLogEntry("logs/system.log");

    EXPECT_EQ(logEntry["level"], "INFO");
    EXPECT_EQ(logEntry["source"], "cpp");
    EXPECT_EQ(logEntry["message"], "Test info message");
}

TEST(LoggerTest, LogsErrorMessage) {
    Logger::log("ERROR", "cpp", "Test error message");

    auto logEntry = getLastLogEntry("logs/system.log");

    EXPECT_EQ(logEntry["level"], "ERROR");
    EXPECT_EQ(logEntry["source"], "cpp");
    EXPECT_EQ(logEntry["message"], "Test error message");
}