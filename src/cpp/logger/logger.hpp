#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <string>

class Logger {
public:
    static void log(const std::string& level, const std::string& message, const std::string& file, int line);
};


// macro to simplify logging with file and line info
#define LOG(level, source, message) Logger::log(level, source, message, __FILE__, __LINE__)

#endif // LOGGER_HPP