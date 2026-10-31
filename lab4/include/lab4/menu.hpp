/**
 * @file menu.hpp
 * @brief Console menu demonstrating the sorting algorithms and the undirected graph.
 */
#ifndef LAB4_MENU_HPP
#define LAB4_MENU_HPP

#include <functional>
#include <istream>
#include <ostream>
#include <string>
#include <vector>

#include "lab4/graph.hpp"

namespace lab4 {

/** @brief Interactive text menu. Input and output streams are injected so the menu can be tested. */
class Menu {
public:
    /**
     * @brief Creates a menu bound to the given streams.
     * @param input  stream commands are read from.
     * @param output stream the menu and results are written to.
     */
    Menu(std::istream& input, std::ostream& output);

    /** @brief Runs the main menu until the user chooses "0" or the input ends. */
    void run();

private:
    enum class Algorithm { Bubble, Patience };

    struct Command {
        std::string label;
        std::function<void()> action;
    };

    using Graph = UndirectedGraph<std::string>;

    void run_menu(const std::string& title, const std::string& exit_label, const std::vector<Command>& commands);
    void run_graph_menu();
    std::string read_line();
    std::string prompt(const std::string& text);
    std::size_t read_number(const std::string& text);

    Algorithm choose_algorithm();
    void sort_integers();
    void sort_c_array();
    void sort_strings();
    void sort_students();

    Graph::vertex_id read_vertex(const std::string& text);
    void add_vertex();
    void add_edge();
    void remove_vertex();
    void remove_edge();
    void show_graph();
    void show_vertex_degree();
    void show_edge_degree();
    void show_vertices();
    void show_edges();
    void show_incident_edges();
    void show_adjacent_vertices();
    void remove_vertex_by_iterator();
    void remove_edge_by_iterator();
    void rename_vertex();
    void compare_with_copy();
    void clear_graph();
    void fill_demo_graph();

    std::istream& input_;
    std::ostream& output_;
    Graph graph_;
    std::vector<Command> main_commands_;
    std::vector<Command> graph_commands_;
};

}  // namespace lab4

#endif  // LAB4_MENU_HPP
