#include "logger.hpp"
#include <gtest/gtest.h>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>

// helper function to read the last log entry from the log file
std::string getLastLogEntry(const std::string& logFilePath) {
    std::ifstream logFile(logFilePath, std::ios::in);
    std::string lastLine;
    std::string currentLine;

    while (std::getline(logFile, currentLine)) {
        lastLine = currentLine;
    }
    logFile.close();

    return lastLine;
}

// helper function to parse a log entry
struct LogEntry {
    std::string timestamp;
    std::string level;
    std::string source;
    std::string message;
};

LogEntry parseLogEntry(const std::string& logEntry) {
    std::istringstream stream(logEntry);
    LogEntry entry;

    // Parse the log line: [timestamp] [level] [source] message
    std::getline(stream, entry.timestamp, ']');
    entry.timestamp = entry.timestamp.substr(1); // Remove leading '['
    std::getline(stream, entry.level, ']');
    entry.level = entry.level.substr(2); // Remove leading " [" and trailing ']'
    std::getline(stream, entry.source, ']');
    entry.source = entry.source.substr(2); // Remove leading " [" and trailing ']'
    std::getline(stream, entry.message);  // Remaining part is the message
    entry.message = entry.message.substr(1); // Remove leading space

    return entry;
}

// test cases for logger
TEST(LoggerTest, LogsInfoMessage) {
    Logger::log("INFO", "Test info message");

    auto lastLogLine = getLastLogEntry("logs/system.log");
    auto logEntry = parseLogEntry(lastLogLine);

    EXPECT_EQ(logEntry.level, "INFO");
    EXPECT_EQ(logEntry.source, __FILE__);
    EXPECT_EQ(logEntry.message, "Test info message");
}

TEST(LoggerTest, LogsErrorMessage) {
    Logger::log("ERROR", "Test error message");

    auto lastLogLine = getLastLogEntry("logs/system.log");
    auto logEntry = parseLogEntry(lastLogLine);

    EXPECT_EQ(logEntry.level, "ERROR");
    EXPECT_EQ(logEntry.source, __FILE__);
    EXPECT_EQ(logEntry.message, "Test error message");
}

TEST(LoggerTest, LogsWarningMessage) {
    Logger::log("WARNING", "Test warning message");

    auto lastLogLine = getLastLogEntry("logs/system.log");
    auto logEntry = parseLogEntry(lastLogLine);

    EXPECT_EQ(logEntry.level, "WARNING");
    EXPECT_EQ(logEntry.source, __FILE__);
    EXPECT_EQ(logEntry.message, "Test warning message");
}