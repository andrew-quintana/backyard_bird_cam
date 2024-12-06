#include <pybind11/pybind11.h>
#include "logger.hpp"

namespace py = pybind11;

PYBIND11_MODULE(logger_bindings, m) {
    m.doc() = "Python bindings for the C++ Logger";

    m.def("log", &Logger::log, "Log a message",
          py::arg("level"),
          py::arg("source"),
          py::arg("message"));
}