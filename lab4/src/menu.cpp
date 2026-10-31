/** @file menu.cpp
 *  @brief Implementation of lab4::Menu. */
#include "lab4/menu.hpp"

#include <algorithm>
#include <cctype>
#include <exception>
#include <iterator>
#include <sstream>
#include <stdexcept>

#include "lab4/sorting.hpp"
#include "lab4/student.hpp"

namespace lab4 {

namespace {

const char* const kExitChoice = "0";
const char* const kItemSeparator = ", ";
const int kDemoNumbers[] = {5, 3, 9, 1, 7, 2};
const Student kDemoStudents[] = {{"Petrov", 20, 4.1}, {"Ivanov", 19, 4.8}, {"Sidorov", 21, 3.9}, {"Ivanov", 18, 4.5}};
const char* const kDemoVertexNames[] = {"A", "B", "C", "D"};
const std::pair<std::size_t, std::size_t> kDemoEdges[] = {{0, 1}, {1, 2}, {2, 3}, {0, 2}};

template <typename Range, typename Compare = std::less<>>
void sort_with(bool use_bubble, Range& range, Compare comp = Compare())
{
    if (use_bubble) {
        bubble_sort(range, comp);
    } else {
        patience_sort(range, comp);
    }
}

int parse_int(const std::string& text)
{
    try {
        std::size_t used = 0;
        int number = std::stoi(text, &used);
        if (used == text.size()) {
            return number;
        }
    } catch (const std::logic_error&) {
        // falls through to the common error below
    }
    throw std::invalid_argument("Not a valid integer: " + text);
}

template <typename Iterator>
std::string join(Iterator first, Iterator last)
{
    std::ostringstream text;
    bool is_first = true;
    std::for_each(first, last, [&](const auto& item) {
        text << (is_first ? "" : kItemSeparator) << item;
        is_first = false;
    });
    return text.str();
}

template <typename Iterator>
std::string join_vertices(Iterator first, Iterator last)
{
    std::ostringstream text;
    bool is_first = true;
    std::for_each(first, last, [&](const auto& vertex) {
        text << (is_first ? "" : kItemSeparator) << vertex.id << ':' << vertex.value;
        is_first = false;
    });
    return text.str();
}

template <typename Iterator>
std::string join_edges(Iterator first, Iterator last)
{
    std::ostringstream text;
    bool is_first = true;
    std::for_each(first, last, [&](const auto& edge) {
        text << (is_first ? "" : kItemSeparator) << edge.first << '-' << edge.second;
        is_first = false;
    });
    return text.str();
}

}  // namespace

Menu::Menu(std::istream& input, std::ostream& output) : input_(input), output_(output)
{
    main_commands_ = {
        {"Sort integers (std::vector)", [this] { sort_integers(); }},
        {"Sort a built-in C array", [this] { sort_c_array(); }},
        {"Sort strings (std::vector<std::string>)", [this] { sort_strings(); }},
        {"Sort students (custom class)", [this] { sort_students(); }},
        {"Graph (undirected, adjacency matrix)", [this] { run_graph_menu(); }},
    };
    graph_commands_ = {
        {"Add vertex", [this] { add_vertex(); }},
        {"Add edge", [this] { add_edge(); }},
        {"Remove vertex", [this] { remove_vertex(); }},
        {"Remove edge", [this] { remove_edge(); }},
        {"Show graph", [this] { show_graph(); }},
        {"Vertex degree", [this] { show_vertex_degree(); }},
        {"Edge degree", [this] { show_edge_degree(); }},
        {"Iterate vertices (forward / reverse)", [this] { show_vertices(); }},
        {"Iterate edges (forward / reverse)", [this] { show_edges(); }},
        {"Iterate edges incident to a vertex", [this] { show_incident_edges(); }},
        {"Iterate vertices adjacent to a vertex", [this] { show_adjacent_vertices(); }},
        {"Remove vertex via iterator", [this] { remove_vertex_by_iterator(); }},
        {"Remove edge via iterator", [this] { remove_edge_by_iterator(); }},
        {"Rename vertex via iterator", [this] { rename_vertex(); }},
        {"Copy and compare graphs", [this] { compare_with_copy(); }},
        {"Clear graph", [this] { clear_graph(); }},
        {"Fill demo graph", [this] { fill_demo_graph(); }},
    };
}

void Menu::run() { run_menu("Main menu", "Exit", main_commands_); }

void Menu::run_graph_menu() { run_menu("Graph menu", "Back", graph_commands_); }

void Menu::run_menu(const std::string& title, const std::string& exit_label, const std::vector<Command>& commands)
{
    while (true) {
        output_ << "=== " << title << " ===\n";
        for (std::size_t index = 0; index < commands.size(); ++index) {
            output_ << index + 1 << ". " << commands[index].label << '\n';
        }
        output_ << kExitChoice << ". " << exit_label << '\n';

        std::string choice = read_line();
        if (choice == kExitChoice) {
            return;
        }
        bool is_number = !choice.empty() && std::all_of(choice.begin(), choice.end(), [](unsigned char symbol) {
            return std::isdigit(symbol) != 0;
        });
        std::size_t number = is_number && choice.size() < 9 ? std::stoul(choice) : 0;
        if (number < 1 || number > commands.size()) {
            output_ << "Unknown command.\n";
            continue;
        }
        try {
            commands[number - 1].action();
        } catch (const std::exception& error) {
            output_ << "Error: " << error.what() << '\n';
        }
    }
}

std::string Menu::read_line()
{
    std::string line;
    if (!std::getline(input_, line)) {
        return kExitChoice;
    }
    std::size_t begin = line.find_first_not_of(" \t\r");
    std::size_t end = line.find_last_not_of(" \t\r");
    return begin == std::string::npos ? std::string() : line.substr(begin, end - begin + 1);
}

std::string Menu::prompt(const std::string& text)
{
    output_ << text;
    return read_line();
}

std::size_t Menu::read_number(const std::string& text)
{
    std::string line = prompt(text);
    bool is_number = !line.empty() && line.size() < 9 && std::all_of(line.begin(), line.end(), [](unsigned char symbol) {
        return std::isdigit(symbol) != 0;
    });
    if (!is_number) {
        throw std::invalid_argument("Not a valid number: " + line);
    }
    return std::stoul(line);
}

// ---------- sorting ----------

Menu::Algorithm Menu::choose_algorithm()
{
    output_ << "1. Bubble sort\n2. Patience sort\n";
    std::string choice = prompt("Algorithm: ");
    if (choice == "1") {
        return Algorithm::Bubble;
    }
    if (choice == "2") {
        return Algorithm::Patience;
    }
    throw std::invalid_argument("Unknown algorithm.");
}

void Menu::sort_integers()
{
    bool use_bubble = choose_algorithm() == Algorithm::Bubble;
    std::istringstream line(prompt("Enter integers separated by spaces: "));
    std::vector<int> numbers;
    std::string token;
    while (line >> token) {
        numbers.push_back(parse_int(token));
    }
    sort_with(use_bubble, numbers);
    output_ << (use_bubble ? "Bubble sort: " : "Patience sort: ") << join(numbers.begin(), numbers.end()) << '\n';
}

void Menu::sort_c_array()
{
    bool use_bubble = choose_algorithm() == Algorithm::Bubble;
    int numbers[sizeof(kDemoNumbers) / sizeof(kDemoNumbers[0])];
    std::copy(std::begin(kDemoNumbers), std::end(kDemoNumbers), std::begin(numbers));
    output_ << "Before: " << join(std::begin(numbers), std::end(numbers)) << '\n';
    sort_with(use_bubble, numbers);
    output_ << (use_bubble ? "Bubble sort: " : "Patience sort: ") << join(std::begin(numbers), std::end(numbers))
            << '\n';
}

void Menu::sort_strings()
{
    bool use_bubble = choose_algorithm() == Algorithm::Bubble;
    std::istringstream line(prompt("Enter words separated by spaces: "));
    std::vector<std::string> words{std::istream_iterator<std::string>(line), std::istream_iterator<std::string>()};
    sort_with(use_bubble, words);
    output_ << (use_bubble ? "Bubble sort: " : "Patience sort: ") << join(words.begin(), words.end()) << '\n';
}

void Menu::sort_students()
{
    bool use_bubble = choose_algorithm() == Algorithm::Bubble;
    output_ << "1. By name and age\n2. By grade (descending)\n";
    std::string order = prompt("Order: ");
    if (order != "1" && order != "2") {
        throw std::invalid_argument("Unknown order.");
    }
    std::vector<Student> students(std::begin(kDemoStudents), std::end(kDemoStudents));
    if (order == "1") {
        sort_with(use_bubble, students);
    } else {
        sort_with(use_bubble, students, ByGradeDescending());
    }
    output_ << (use_bubble ? "Bubble sort:" : "Patience sort:") << '\n';
    std::copy(students.begin(), students.end(), std::ostream_iterator<Student>(output_, "\n"));
}

// ---------- graph ----------

Menu::Graph::vertex_id Menu::read_vertex(const std::string& text)
{
    Graph::vertex_id id = read_number(text);
    if (!graph_.contains_vertex(id)) {
        throw std::out_of_range("vertex not found");
    }
    return id;
}

void Menu::add_vertex()
{
    Graph::vertex_id id = graph_.add_vertex(prompt("Vertex value: "));
    output_ << "Added vertex " << id << ':' << graph_.value(id) << '\n';
}

void Menu::add_edge()
{
    Graph::vertex_id first = read_vertex("First vertex id: ");
    Graph::vertex_id second = read_vertex("Second vertex id: ");
    graph_.add_edge(first, second);
    output_ << "Added edge " << first << '-' << second << '\n';
}

void Menu::remove_vertex()
{
    graph_.remove_vertex(read_vertex("Vertex id: "));
    output_ << "Vertex removed.\n";
}

void Menu::remove_edge()
{
    Graph::vertex_id first = read_vertex("First vertex id: ");
    Graph::vertex_id second = read_vertex("Second vertex id: ");
    graph_.remove_edge(first, second);
    output_ << "Edge removed.\n";
}

void Menu::show_graph()
{
    output_ << graph_ << '\n';
    output_ << "Empty: " << (graph_.empty() ? "True" : "False") << '\n';
}

void Menu::show_vertex_degree()
{
    Graph::vertex_id id = read_vertex("Vertex id: ");
    output_ << "Degree: " << graph_.vertex_degree(id) << '\n';
}

void Menu::show_edge_degree()
{
    Graph::vertex_id first = read_vertex("First vertex id: ");
    Graph::vertex_id second = read_vertex("Second vertex id: ");
    output_ << "Edge degree: " << graph_.edge_degree(first, second) << '\n';
}

void Menu::show_vertices()
{
    const Graph& graph = graph_;
    output_ << "Forward: " << join_vertices(graph.vertices_cbegin(), graph.vertices_cend()) << '\n';
    output_ << "Reverse: " << join_vertices(graph.vertices_crbegin(), graph.vertices_crend()) << '\n';
}

void Menu::show_edges()
{
    const Graph& graph = graph_;
    output_ << "Forward: " << join_edges(graph.edges_cbegin(), graph.edges_cend()) << '\n';
    output_ << "Reverse: " << join_edges(graph.edges_crbegin(), graph.edges_crend()) << '\n';
}

void Menu::show_incident_edges()
{
    const Graph& graph = graph_;
    Graph::vertex_id id = read_vertex("Vertex id: ");
    output_ << "Forward: " << join_edges(graph.incident_cbegin(id), graph.incident_cend(id)) << '\n';
    output_ << "Reverse: " << join_edges(graph.incident_crbegin(id), graph.incident_crend(id)) << '\n';
}

void Menu::show_adjacent_vertices()
{
    const Graph& graph = graph_;
    Graph::vertex_id id = read_vertex("Vertex id: ");
    output_ << "Forward: " << join_vertices(graph.adjacent_cbegin(id), graph.adjacent_cend(id)) << '\n';
    output_ << "Reverse: " << join_vertices(graph.adjacent_crbegin(id), graph.adjacent_crend(id)) << '\n';
}

void Menu::remove_vertex_by_iterator()
{
    std::size_t position = read_number("Vertex position (1-based): ");
    if (position < 1 || position > graph_.vertex_count()) {
        throw std::out_of_range("position is out of range");
    }
    Graph::vertex_iterator iterator = graph_.vertices_begin();
    std::advance(iterator, static_cast<std::ptrdiff_t>(position - 1));
    graph_.erase_vertex(iterator);
    output_ << "Vertex removed via iterator.\n";
}

void Menu::remove_edge_by_iterator()
{
    std::size_t position = read_number("Edge position (1-based): ");
    if (position < 1 || position > graph_.edge_count()) {
        throw std::out_of_range("position is out of range");
    }
    Graph::edge_iterator iterator = graph_.edges_begin();
    std::advance(iterator, static_cast<std::ptrdiff_t>(position - 1));
    graph_.erase_edge(iterator);
    output_ << "Edge removed via iterator.\n";
}

void Menu::rename_vertex()
{
    std::size_t position = read_number("Vertex position (1-based): ");
    if (position < 1 || position > graph_.vertex_count()) {
        throw std::out_of_range("position is out of range");
    }
    Graph::vertex_iterator iterator = graph_.vertices_begin();
    std::advance(iterator, static_cast<std::ptrdiff_t>(position - 1));
    (*iterator).value = prompt("New value: ");
    output_ << "Vertex renamed via iterator.\n";
}

void Menu::compare_with_copy()
{
    auto flag = [](bool value) { return value ? "True" : "False"; };
    Graph copy(graph_);
    output_ << "Copy equals original: " << flag(copy == graph_) << '\n';
    copy.add_vertex("extra");
    output_ << "After adding a vertex to the copy: == " << flag(copy == graph_) << ", != " << flag(copy != graph_)
            << ", > " << flag(copy > graph_) << '\n';
    output_ << "                                   < " << flag(copy < graph_) << ", >= " << flag(copy >= graph_)
            << ", <= " << flag(copy <= graph_) << '\n';
    copy = graph_;
    output_ << "After assignment equals original: " << flag(copy == graph_) << '\n';
}

void Menu::clear_graph()
{
    graph_.clear();
    output_ << "Graph cleared.\n";
}

void Menu::fill_demo_graph()
{
    graph_.clear();
    std::vector<Graph::vertex_id> ids;
    for (const char* name : kDemoVertexNames) {
        ids.push_back(graph_.add_vertex(name));
    }
    for (const auto& edge : kDemoEdges) {
        graph_.add_edge(ids[edge.first], ids[edge.second]);
    }
    output_ << "Demo graph created.\n";
}

}  // namespace lab4
