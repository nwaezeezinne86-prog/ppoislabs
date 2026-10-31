/**
 * @file test_framework.hpp
 * @brief Minimal self-contained unit-test framework (no external dependencies, runs from the console).
 */
#ifndef LAB4_TEST_FRAMEWORK_HPP
#define LAB4_TEST_FRAMEWORK_HPP

#include <exception>
#include <functional>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace testing {

/** @brief Thrown by the CHECK macros when an assertion fails. */
struct Failure {
    std::string message;
};

/** @brief A registered test case. */
struct Case {
    std::string name;
    std::function<void()> body;
};

/** @brief Global list of test cases. */
inline std::vector<Case>& registry()
{
    static std::vector<Case> cases;
    return cases;
}

/** @brief Registers a test case at static-initialisation time. */
struct Registrar {
    Registrar(const char* name, std::function<void()> body) { registry().push_back({name, std::move(body)}); }
};

/** @brief Runs every registered test; returns 0 when all pass, 1 otherwise. */
inline int run_all()
{
    int failed = 0;
    for (const Case& test : registry()) {
        try {
            test.body();
            std::cout << "[ OK ] " << test.name << '\n';
        } catch (const Failure& failure) {
            ++failed;
            std::cout << "[FAIL] " << test.name << ": " << failure.message << '\n';
        } catch (const std::exception& error) {
            ++failed;
            std::cout << "[FAIL] " << test.name << ": unexpected exception: " << error.what() << '\n';
        }
    }
    std::cout << registry().size() - static_cast<std::size_t>(failed) << '/' << registry().size() << " tests passed\n";
    return failed == 0 ? 0 : 1;
}

/** @brief Converts a value to text for failure messages. */
template <typename Value>
std::string show(const Value& value)
{
    std::ostringstream text;
    text << value;
    return text.str();
}

}  // namespace testing

#define TEST(name)                                                  \
    static void name();                                             \
    static testing::Registrar registrar_##name(#name, name);        \
    static void name()

#define CHECK(condition)                                                                              \
    do {                                                                                              \
        if (!(condition)) {                                                                           \
            throw testing::Failure{std::string(__FILE__) + ":" + std::to_string(__LINE__) +           \
                                   ": CHECK(" #condition ") failed"};                                 \
        }                                                                                             \
    } while (false)

#define CHECK_EQ(actual, expected)                                                                    \
    do {                                                                                              \
        if (!((actual) == (expected))) {                                                              \
            throw testing::Failure{std::string(__FILE__) + ":" + std::to_string(__LINE__) +           \
                                   ": expected " + testing::show(expected) + " but got " +            \
                                   testing::show(actual)};                                            \
        }                                                                                             \
    } while (false)

#define CHECK_THROWS(expression, ExceptionType)                                                       \
    do {                                                                                              \
        bool thrown_ = false;                                                                         \
        try {                                                                                         \
            (void)(expression);                                                                       \
        } catch (const ExceptionType&) {                                                              \
            thrown_ = true;                                                                           \
        }                                                                                             \
        if (!thrown_) {                                                                               \
            throw testing::Failure{std::string(__FILE__) + ":" + std::to_string(__LINE__) +           \
                                   ": " #expression " did not throw " #ExceptionType};                \
        }                                                                                             \
    } while (false)

#endif  // LAB4_TEST_FRAMEWORK_HPP
