#ifndef LOGGER_HPP
#define LOGGER_HPP

#include <string>

class Logger {
public:
    static void log(const std::string& level, const std::string& source, const std::string& message);
};

#endif // LOGGER_HPP