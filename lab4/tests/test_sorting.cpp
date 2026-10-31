/** @file test_sorting.cpp
 *  @brief Unit tests for bubble_sort and patience_sort. */
#include <algorithm>
#include <array>
#include <functional>
#include <list>
#include <random>
#include <string>
#include <vector>

#include "lab4/sorting.hpp"
#include "lab4/student.hpp"
#include "test_framework.hpp"

namespace {

using lab4::Student;

const unsigned kSeed = 42;
const int kRuns = 40;
const int kMaxLength = 120;
const int kValueRange = 60;

std::vector<std::vector<int>> fixed_cases()
{
    return {{}, {1}, {2, 1}, {1, 2, 3, 4, 5}, {5, 4, 3, 2, 1}, {3, 3, 3, 3}, {4, -2, 7, 0, -2, 9, 4, 1}};
}

template <typename Sorter>
void check_vectors(Sorter sorter)
{
    for (std::vector<int> actual : fixed_cases()) {
        std::vector<int> expected = actual;
        std::sort(expected.begin(), expected.end());
        sorter(actual);
        CHECK(actual == expected);
    }
}

template <typename Sorter>
void check_random(Sorter sorter)
{
    std::mt19937 random(kSeed);
    for (int run = 0; run < kRuns; ++run) {
        std::vector<int> actual(random() % kMaxLength);
        for (int& value : actual) {
            value = static_cast<int>(random() % (2 * kValueRange)) - kValueRange;
        }
        std::vector<int> expected = actual;
        std::sort(expected.begin(), expected.end());
        sorter(actual);
        CHECK(actual == expected);
    }
}

std::vector<Student> students()
{
    return {{"Petrov", 20, 4.1}, {"Ivanov", 19, 4.8}, {"Ivanov", 18, 4.5}};
}

}  // namespace

TEST(bubble_sort_vector_fixed_cases) { check_vectors([](std::vector<int>& v) { lab4::bubble_sort(v); }); }
TEST(patience_sort_vector_fixed_cases) { check_vectors([](std::vector<int>& v) { lab4::patience_sort(v); }); }
TEST(bubble_sort_vector_random) { check_random([](std::vector<int>& v) { lab4::bubble_sort(v); }); }
TEST(patience_sort_vector_random) { check_random([](std::vector<int>& v) { lab4::patience_sort(v); }); }

TEST(sorts_c_arrays)
{
    int bubble[] = {5, 2, 9, 1, 7};
    int patience[] = {5, 2, 9, 1, 7};
    lab4::bubble_sort(bubble);
    lab4::patience_sort(patience);
    CHECK(std::is_sorted(std::begin(bubble), std::end(bubble)));
    CHECK(std::is_sorted(std::begin(patience), std::end(patience)));
}

TEST(sorts_std_array_and_iterator_range)
{
    std::array<double, 4> values = {2.5, -1.0, 3.75, 0.0};
    lab4::patience_sort(values.begin(), values.end());
    CHECK(std::is_sorted(values.begin(), values.end()));
    std::array<double, 4> other = {2.5, -1.0, 3.75, 0.0};
    lab4::bubble_sort(other.begin(), other.end());
    CHECK(values == other);
}

TEST(sorts_forward_only_list)
{
    std::list<int> numbers = {4, 1, 3, 2};
    lab4::bubble_sort(numbers);
    CHECK(std::is_sorted(numbers.begin(), numbers.end()));
    std::list<int> more = {9, 8, 7, 1};
    lab4::patience_sort(more);
    CHECK(std::is_sorted(more.begin(), more.end()));
}

TEST(sorts_strings_with_custom_comparator)
{
    std::vector<std::string> words = {"pear", "fig", "apple"};
    lab4::bubble_sort(words, std::greater<std::string>());
    CHECK((words == std::vector<std::string>{"pear", "fig", "apple"}));
    lab4::patience_sort(words, std::less<std::string>());
    CHECK((words == std::vector<std::string>{"apple", "fig", "pear"}));
}

TEST(sorts_students_by_natural_order)
{
    std::vector<Student> bubble = students();
    std::vector<Student> patience = students();
    lab4::bubble_sort(bubble);
    lab4::patience_sort(patience);
    CHECK_EQ(bubble.front().age, 18);
    CHECK_EQ(bubble.back().name, std::string("Petrov"));
    CHECK(bubble == patience);
}

TEST(sorts_students_by_grade_descending)
{
    std::vector<Student> list = students();
    lab4::patience_sort(list, lab4::ByGradeDescending());
    CHECK(list[0].average_grade == 4.8 && list[1].average_grade == 4.5 && list[2].average_grade == 4.1);
    lab4::bubble_sort(list, [](const Student& a, const Student& b) { return a.age < b.age; });
    CHECK_EQ(list[0].age, 18);
}

TEST(bubble_sort_is_stable)
{
    std::vector<Student> list = {{"A", 30, 1.0}, {"A", 30, 2.0}, {"A", 30, 3.0}};
    lab4::bubble_sort(list, [](const Student& a, const Student& b) { return a.name < b.name; });
    CHECK(list[0].average_grade == 1.0 && list[1].average_grade == 2.0 && list[2].average_grade == 3.0);
}

TEST(student_comparison_and_printing)
{
    Student ivanov{"Ivanov", 18, 4.5};
    CHECK(ivanov < Student({"Ivanov", 19, 1.0}));
    CHECK(!(Student({"Petrov", 1, 1.0}) < ivanov));
    CHECK(ivanov == Student({"Ivanov", 18, 4.5}));
    CHECK_EQ(testing::show(ivanov), std::string("Ivanov (18), grade 4.50"));
}
