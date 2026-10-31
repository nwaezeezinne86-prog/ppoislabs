/** @file test_menu.cpp
 *  @brief Scenario tests for the console menu (input and output are string streams). */
#include <sstream>
#include <string>
#include <vector>

#include "lab4/menu.hpp"
#include "test_framework.hpp"

namespace {

const std::string kDemoGraphText = "Graph(V=4, E=4) vertices: [0:A, 1:B, 2:C, 3:D] edges: [0-1, 0-2, 1-2, 2-3]";

std::string run(const std::vector<std::string>& lines)
{
    std::string script;
    for (const std::string& line : lines) {
        script += line + "\n";
    }
    std::istringstream input(script);
    std::ostringstream output;
    lab4::Menu menu(input, output);
    menu.run();
    return output.str();
}

/** Opens the graph submenu (5), runs the commands, leaves the submenu and the program. */
std::string run_graph(std::vector<std::string> commands)
{
    commands.insert(commands.begin(), "5");
    commands.push_back("0");
    commands.push_back("0");
    return run(commands);
}

/** Same as run_graph, but fills the demo graph first (command 17). */
std::string run_demo(std::vector<std::string> commands)
{
    commands.insert(commands.begin(), "17");
    return run_graph(commands);
}

bool contains(const std::string& text, const std::string& part) { return text.find(part) != std::string::npos; }

bool appears_before(const std::string& text, const std::string& first, const std::string& second)
{
    return text.find(first) < text.find(second);
}

}  // namespace

TEST(menu_exit_and_end_of_input)
{
    CHECK(contains(run({"0"}), "=== Main menu ==="));
    CHECK(contains(run({}), "=== Main menu ==="));
}

TEST(menu_reports_unknown_commands)
{
    std::string output = run({"9", "abc", "-1", "", "0"});
    CHECK(contains(output, "Unknown command."));
}

TEST(menu_sorts_integers_with_both_algorithms)
{
    CHECK(contains(run({"1", "1", "5 3 1 4", "0"}), "Bubble sort: 1, 3, 4, 5"));
    CHECK(contains(run({"1", "2", "5 3 1 4", "0"}), "Patience sort: 1, 3, 4, 5"));
}

TEST(menu_reports_bad_integer_input)
{
    CHECK(contains(run({"1", "1", "5 x", "0"}), "Error: Not a valid integer: x"));
    CHECK(contains(run({"1", "1", "99999999999", "0"}), "Error: Not a valid integer"));
    CHECK(contains(run({"1", "7", "0"}), "Error: Unknown algorithm."));
}

TEST(menu_sorts_c_array)
{
    std::string output = run({"2", "1", "2", "2", "0"});
    CHECK(contains(output, "Before: 5, 3, 9, 1, 7, 2"));
    CHECK(contains(output, "Bubble sort: 1, 2, 3, 5, 7, 9"));
    CHECK(contains(output, "Patience sort: 1, 2, 3, 5, 7, 9"));
}

TEST(menu_sorts_strings)
{
    CHECK(contains(run({"3", "1", "pear apple fig", "0"}), "Bubble sort: apple, fig, pear"));
    CHECK(contains(run({"3", "2", "pear apple fig", "0"}), "Patience sort: apple, fig, pear"));
}

TEST(menu_sorts_students)
{
    std::string natural = run({"4", "1", "1", "0"});
    CHECK(appears_before(natural, "Ivanov (18), grade 4.50", "Petrov (20), grade 4.10"));
    std::string by_grade = run({"4", "2", "2", "0"});
    CHECK(appears_before(by_grade, "Ivanov (19), grade 4.80", "Ivanov (18), grade 4.50"));
    CHECK(contains(run({"4", "1", "9", "0"}), "Error: Unknown order."));
}

TEST(menu_graph_fill_and_show)
{
    std::string output = run_demo({"5"});
    CHECK(contains(output, "Demo graph created."));
    CHECK(contains(output, kDemoGraphText));
    CHECK(contains(output, "Empty: False"));
}

TEST(menu_graph_add_vertices_and_edge)
{
    std::string output = run_graph({"1", "X", "1", "Y", "2", "0", "1", "5"});
    CHECK(contains(output, "Added vertex 0:X"));
    CHECK(contains(output, "Added edge 0-1"));
}

TEST(menu_graph_remove_vertex_and_edge)
{
    std::string removed_vertex = run_demo({"3", "1", "5"});
    CHECK(contains(removed_vertex, "Vertex removed."));
    CHECK(contains(removed_vertex, "vertices: [0:A, 2:C, 3:D] edges: [0-2, 2-3]"));
    std::string removed_edge = run_demo({"4", "0", "1", "5"});
    CHECK(contains(removed_edge, "Edge removed."));
    CHECK(contains(removed_edge, "edges: [0-2, 1-2, 2-3]"));
}

TEST(menu_graph_degrees)
{
    std::string output = run_demo({"6", "2", "7", "0", "1"});
    CHECK(contains(output, "Degree: 3"));
    CHECK(contains(output, "Edge degree: 2"));
}

TEST(menu_graph_iterates_vertices_and_edges)
{
    std::string output = run_demo({"8", "9"});
    CHECK(contains(output, "Forward: 0:A, 1:B, 2:C, 3:D"));
    CHECK(contains(output, "Reverse: 3:D, 2:C, 1:B, 0:A"));
    CHECK(contains(output, "Forward: 0-1, 0-2, 1-2, 2-3"));
    CHECK(contains(output, "Reverse: 2-3, 1-2, 0-2, 0-1"));
}

TEST(menu_graph_iterates_incident_and_adjacent)
{
    std::string output = run_demo({"10", "2", "11", "2"});
    CHECK(contains(output, "Forward: 2-0, 2-1, 2-3"));
    CHECK(contains(output, "Reverse: 2-3, 2-1, 2-0"));
    CHECK(contains(output, "Forward: 0:A, 1:B, 3:D"));
    CHECK(contains(output, "Reverse: 3:D, 1:B, 0:A"));
}

TEST(menu_graph_removes_vertex_via_iterator)
{
    std::string output = run_demo({"12", "2", "5"});
    CHECK(contains(output, "Vertex removed via iterator."));
    CHECK(contains(output, "vertices: [0:A, 2:C, 3:D]"));
    CHECK(contains(run_demo({"12", "9"}), "Error: position is out of range"));
}

TEST(menu_graph_removes_edge_via_iterator)
{
    std::string output = run_demo({"13", "1", "5"});
    CHECK(contains(output, "Edge removed via iterator."));
    CHECK(contains(output, "edges: [0-2, 1-2, 2-3]"));
    CHECK(contains(run_demo({"13", "0"}), "Error: position is out of range"));
}

TEST(menu_graph_renames_vertex_via_iterator)
{
    std::string output = run_demo({"14", "1", "Z", "5"});
    CHECK(contains(output, "Vertex renamed via iterator."));
    CHECK(contains(output, "vertices: [0:Z, 1:B, 2:C, 3:D]"));
    CHECK(contains(run_demo({"14", "7"}), "Error: position is out of range"));
}

TEST(menu_graph_copy_and_compare)
{
    std::string output = run_demo({"15"});
    CHECK(contains(output, "Copy equals original: True"));
    CHECK(contains(output, "== False, != True, > True"));
    CHECK(contains(output, "< False, >= True, <= False"));
    CHECK(contains(output, "After assignment equals original: True"));
}

TEST(menu_graph_clear)
{
    std::string output = run_demo({"16", "5"});
    CHECK(contains(output, "Graph cleared."));
    CHECK(contains(output, "Empty: True"));
}

TEST(menu_graph_reports_errors)
{
    CHECK(contains(run_graph({"2", "0", "1"}), "Error: vertex not found"));
    CHECK(contains(run_demo({"6", "x"}), "Error: Not a valid number: x"));
    CHECK(contains(run_demo({"2", "0", "0"}), "Error: loops are not supported"));
    CHECK(contains(run_graph({"99"}), "Unknown command."));
}
