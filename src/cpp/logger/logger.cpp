#include "logger.hpp"
#include <fstream>
#include <ctime>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

void Logger::log(const std::string& level, const std::string& source, const std::string& message) {
    std::ofstream logFile("logs/system.log", std::ios::app);
    if (logFile.is_open()) {
        json logEntry;
        std::time_t now = std::time(nullptr);
        logEntry["timestamp"] = std::asctime(std::localtime(&now)); // ISO 8601 preferred
        logEntry["level"] = level;
        logEntry["source"] = source;
        logEntry["message"] = message;

        logFile << logEntry.dump() << std::endl;
        logFile.close();
    } else {
        std::cerr << "Error: Unable to open log file." << std::endl;
    }
}