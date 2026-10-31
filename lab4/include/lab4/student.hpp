/**
 * @file student.hpp
 * @brief Demo user-defined type used to show sorting of custom objects.
 */
#ifndef LAB4_STUDENT_HPP
#define LAB4_STUDENT_HPP

#include <iomanip>
#include <ostream>
#include <sstream>
#include <string>

namespace lab4 {

/** @brief A student; natural order is by name, then by age. */
struct Student {
    std::string name;     ///< Student name.
    int age = 0;          ///< Age in years.
    double average_grade = 0.0;  ///< Average grade.
};

/** @brief Natural order: name first, then age. */
inline bool operator<(const Student& left, const Student& right)
{
    if (left.name != right.name) {
        return left.name < right.name;
    }
    return left.age < right.age;
}

/** @brief Equality of all fields. */
inline bool operator==(const Student& left, const Student& right)
{
    return left.name == right.name && left.age == right.age && left.average_grade == right.average_grade;
}

/** @brief Prints `Name (age), grade X.XX`. */
inline std::ostream& operator<<(std::ostream& out, const Student& student)
{
    std::ostringstream text;
    text << student.name << " (" << student.age << "), grade " << std::fixed << std::setprecision(2)
         << student.average_grade;
    return out << text.str();
}

/** @brief Comparator: higher average grade first. */
struct ByGradeDescending {
    /** @brief Returns true when @p left has a strictly higher grade than @p right. */
    bool operator()(const Student& left, const Student& right) const
    {
        return left.average_grade > right.average_grade;
    }
};

}  // namespace lab4

#endif  // LAB4_STUDENT_HPP
