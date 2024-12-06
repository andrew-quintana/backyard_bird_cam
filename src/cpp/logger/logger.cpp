#include "logger.hpp"
#include <fstream>
#include <iostream>
#include <filesystem>
#include <ctime>
#include <iomanip>
#include <sstream>

// ansi color codes
#define RESET   "\033[0m"
#define RED     "\033[31m"
#define YELLOW  "\033[33m"
#define NORMAL  "\033[0m"

// macro to simplify logging calls
#define LOG(level, source, message) Logger::log(level, source, message, __FILE__, __LINE__)

void Logger::log(const std::string& level, const std::string& message, const std::string& file, int line) {
    // define the log file path
    const std::string logDirPath = "logs";
    const std::string logFilePath = logDirPath + "/system.log";

    // ensure the logs directory exists
    if (!std::filesystem::exists(logDirPath)) {
        if (!std::filesystem::create_directories(logDirPath)) {
            std::cerr << "Error: Unable to create directory: " << logDirPath << std::endl;
            return;
        }
    }

    // get the current time
    std::time_t now = std::time(nullptr);
    std::tm* localTime = std::localtime(&now);
    std::ostringstream timestamp;
    timestamp << std::put_time(localTime, "%Y-%m-%d %H:%M:%S");

    // format the log message
    std::ostringstream logEntry;
    logEntry << "[" << timestamp.str() << "] "
             << "[" << level << "] "
             << "[" << file << ":" << line << "] "
             << message;

    // write the log message to the log file
    std::ofstream logFile(logFilePath, std::ios::app);
    if (logFile.is_open()) {
        logFile << logEntry.str() << std::endl;
        logFile.close();
    } else {
        std::cerr << "Error: Unable to open log file: " << logFilePath << std::endl;
    }

    // determine color based on log level
    std::string color;
    if (level == "ERROR") {
        color = RED;
    } else if (level == "WARNING") {
        color = YELLOW;
    } else {
        color = NORMAL;
    }

    // format the log message
    std::ostringstream consoleEntry;
    consoleEntry << "[" << timestamp.str() << "] "
             << "[" << level << "] "
             << "[" << file << ":" << line << "] "
             << message;

    // print the log message to the console with color
    std::cout << color << consoleEntry.str() << RESET << std::endl;
}