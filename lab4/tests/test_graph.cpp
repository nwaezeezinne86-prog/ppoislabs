/** @file test_graph.cpp
 *  @brief Unit tests for lab4::UndirectedGraph. */
#include <algorithm>
#include <iterator>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "lab4/graph.hpp"
#include "test_framework.hpp"

namespace {

using Graph = lab4::UndirectedGraph<std::string>;
using Edge = Graph::edge_type;
using Edges = std::vector<Edge>;
using Names = std::vector<std::string>;

const std::size_t kMissing = 99;

/** Sample graph: A-B, B-C, C-D, A-C with identifiers 0..3. */
struct Sample {
    Graph graph;
    Graph::vertex_id a = graph.add_vertex("A");
    Graph::vertex_id b = graph.add_vertex("B");
    Graph::vertex_id c = graph.add_vertex("C");
    Graph::vertex_id d = graph.add_vertex("D");

    Sample()
    {
        graph.add_edge(a, b);
        graph.add_edge(b, c);
        graph.add_edge(c, d);
        graph.add_edge(a, c);
    }
};

template <typename Iterator>
Names names(Iterator first, Iterator last)
{
    Names result;
    for (; first != last; ++first) {
        result.push_back((*first).value);
    }
    return result;
}

template <typename Iterator>
Edges edges(Iterator first, Iterator last)
{
    return Edges(first, last);
}

Edges reversed(Edges items)
{
    std::reverse(items.begin(), items.end());
    return items;
}

Names reversed(Names items)
{
    std::reverse(items.begin(), items.end());
    return items;
}

std::string text(const Graph& graph)
{
    std::ostringstream out;
    out << graph;
    return out.str();
}

}  // namespace

TEST(new_graph_is_empty)
{
    Graph graph;
    CHECK(graph.empty());
    CHECK_EQ(graph.vertex_count(), 0u);
    CHECK_EQ(graph.edge_count(), 0u);
    CHECK(graph.vertices_begin() == graph.vertices_end());
    CHECK(graph.edges_begin() == graph.edges_end());
}

TEST(counts_contains_and_values)
{
    Sample s;
    CHECK(!s.graph.empty());
    CHECK_EQ(s.graph.vertex_count(), 4u);
    CHECK_EQ(s.graph.edge_count(), 4u);
    CHECK(s.graph.contains_vertex(s.a) && !s.graph.contains_vertex(kMissing));
    CHECK(s.graph.contains_edge(s.a, s.b) && s.graph.contains_edge(s.b, s.a));
    CHECK(!s.graph.contains_edge(s.a, s.d) && !s.graph.contains_edge(s.a, kMissing));
    CHECK_EQ(s.graph.value(s.b), std::string("B"));
    s.graph.value(s.b) = "Z";
    const Graph& view = s.graph;
    CHECK_EQ(view.value(s.b), std::string("Z"));
}

TEST(degrees)
{
    Sample s;
    CHECK_EQ(s.graph.vertex_degree(s.a), 2u);
    CHECK_EQ(s.graph.vertex_degree(s.c), 3u);
    CHECK_EQ(s.graph.vertex_degree(s.d), 1u);
    CHECK_EQ(s.graph.edge_degree(s.a, s.b), 2u);
    CHECK_EQ(s.graph.edge_degree(s.a, s.c), 3u);
    CHECK_EQ(s.graph.edge_degree(s.d, s.c), 2u);
}

TEST(printing_uses_iterators)
{
    Sample s;
    CHECK_EQ(text(s.graph), std::string("Graph(V=4, E=4) vertices: [0:A, 1:B, 2:C, 3:D] edges: [0-1, 0-2, 1-2, 2-3]"));
}

TEST(remove_vertex_removes_incident_edges)
{
    Sample s;
    s.graph.remove_vertex(s.b);
    CHECK_EQ(text(s.graph), std::string("Graph(V=3, E=2) vertices: [0:A, 2:C, 3:D] edges: [0-2, 2-3]"));
    CHECK(!s.graph.contains_vertex(s.b));
}

TEST(remove_edge)
{
    Sample s;
    s.graph.remove_edge(s.b, s.a);
    CHECK_EQ(s.graph.edge_count(), 3u);
    CHECK(!s.graph.contains_edge(s.a, s.b));
}

TEST(clear_does_not_reuse_identifiers)
{
    Sample s;
    s.graph.clear();
    CHECK(s.graph.empty());
    CHECK_EQ(s.graph.edge_count(), 0u);
    CHECK_EQ(s.graph.add_vertex("N"), 4u);
    CHECK(!s.graph.contains_vertex(s.a));
}

TEST(add_vertex_keeps_existing_edges)
{
    Sample s;
    Graph::vertex_id extra = s.graph.add_vertex("E");
    CHECK_EQ(s.graph.edge_count(), 4u);
    CHECK_EQ(s.graph.vertex_degree(extra), 0u);
    CHECK(s.graph.contains_edge(s.a, s.b));
}

TEST(invalid_operations_throw)
{
    Sample s;
    CHECK_THROWS(s.graph.add_edge(s.a, s.a), std::invalid_argument);
    CHECK_THROWS(s.graph.add_edge(s.a, s.b), std::invalid_argument);
    CHECK_THROWS(s.graph.add_edge(s.a, kMissing), std::out_of_range);
    CHECK_THROWS(s.graph.remove_vertex(kMissing), std::out_of_range);
    CHECK_THROWS(s.graph.remove_edge(s.a, s.d), std::out_of_range);
    CHECK_THROWS(s.graph.edge_degree(s.a, s.d), std::out_of_range);
    CHECK_THROWS(s.graph.vertex_degree(kMissing), std::out_of_range);
    CHECK_THROWS(s.graph.value(kMissing), std::out_of_range);
    CHECK_THROWS(s.graph.incident_begin(kMissing), std::out_of_range);
    CHECK_THROWS(s.graph.adjacent_begin(kMissing), std::out_of_range);
}

TEST(copy_constructor_is_deep)
{
    Sample s;
    Graph copy(s.graph);
    copy.remove_vertex(s.a);
    CHECK_EQ(s.graph.vertex_count(), 4u);
    CHECK_EQ(copy.vertex_count(), 3u);
    CHECK_EQ(text(s.graph), std::string("Graph(V=4, E=4) vertices: [0:A, 1:B, 2:C, 3:D] edges: [0-1, 0-2, 1-2, 2-3]"));
}

TEST(copy_assignment_replaces_content)
{
    Sample s;
    Graph target;
    target.add_vertex("old");
    target = s.graph;
    CHECK(target == s.graph);
    Graph& self = target;
    target = self;
    CHECK(target == s.graph);
}

TEST(vertex_iterators_forward_and_reverse)
{
    Sample s;
    Graph& g = s.graph;
    const Graph& c = s.graph;
    Names forward = {"A", "B", "C", "D"};
    CHECK(names(g.vertices_begin(), g.vertices_end()) == forward);
    CHECK(names(g.vertices_rbegin(), g.vertices_rend()) == reversed(forward));
    CHECK(names(c.vertices_begin(), c.vertices_end()) == forward);
    CHECK(names(c.vertices_cbegin(), c.vertices_cend()) == forward);
    CHECK(names(c.vertices_rbegin(), c.vertices_rend()) == reversed(forward));
    CHECK(names(c.vertices_crbegin(), c.vertices_crend()) == reversed(forward));
}

TEST(edge_iterators_forward_and_reverse)
{
    Sample s;
    Graph& g = s.graph;
    const Graph& c = s.graph;
    Edges forward = {{0, 1}, {0, 2}, {1, 2}, {2, 3}};
    CHECK(edges(g.edges_begin(), g.edges_end()) == forward);
    CHECK(edges(g.edges_rbegin(), g.edges_rend()) == reversed(forward));
    CHECK(edges(c.edges_begin(), c.edges_end()) == forward);
    CHECK(edges(c.edges_cbegin(), c.edges_cend()) == forward);
    CHECK(edges(c.edges_rbegin(), c.edges_rend()) == reversed(forward));
    CHECK(edges(c.edges_crbegin(), c.edges_crend()) == reversed(forward));
}

TEST(incident_edge_iterators_forward_and_reverse)
{
    Sample s;
    Graph& g = s.graph;
    const Graph& c = s.graph;
    Edges forward = {{2, 0}, {2, 1}, {2, 3}};
    CHECK(edges(g.incident_begin(s.c), g.incident_end(s.c)) == forward);
    CHECK(edges(g.incident_rbegin(s.c), g.incident_rend(s.c)) == reversed(forward));
    CHECK(edges(c.incident_begin(s.c), c.incident_end(s.c)) == forward);
    CHECK(edges(c.incident_cbegin(s.c), c.incident_cend(s.c)) == forward);
    CHECK(edges(c.incident_rbegin(s.c), c.incident_rend(s.c)) == reversed(forward));
    CHECK(edges(c.incident_crbegin(s.c), c.incident_crend(s.c)) == reversed(forward));
}

TEST(adjacent_vertex_iterators_forward_and_reverse)
{
    Sample s;
    Graph& g = s.graph;
    const Graph& c = s.graph;
    Names forward = {"A", "B", "D"};
    CHECK(names(g.adjacent_begin(s.c), g.adjacent_end(s.c)) == forward);
    CHECK(names(g.adjacent_rbegin(s.c), g.adjacent_rend(s.c)) == reversed(forward));
    CHECK(names(c.adjacent_begin(s.c), c.adjacent_end(s.c)) == forward);
    CHECK(names(c.adjacent_cbegin(s.c), c.adjacent_cend(s.c)) == forward);
    CHECK(names(c.adjacent_rbegin(s.c), c.adjacent_rend(s.c)) == reversed(forward));
    CHECK(names(c.adjacent_crbegin(s.c), c.adjacent_crend(s.c)) == reversed(forward));
}

TEST(iterators_are_bidirectional_and_support_post_increment)
{
    Sample s;
    Graph::vertex_iterator vertex = s.graph.vertices_begin();
    Graph::vertex_iterator old = vertex++;
    CHECK_EQ((*old).value, std::string("A"));
    CHECK_EQ((*vertex).value, std::string("B"));
    vertex--;
    CHECK_EQ((*vertex).id, 0u);
    CHECK(--s.graph.vertices_end() != s.graph.vertices_begin());

    Graph::edge_iterator edge = s.graph.edges_begin();
    CHECK((*edge++) == Edge(0, 1));
    CHECK((*edge--) == Edge(0, 2));
    CHECK((*edge) == Edge(0, 1));

    Graph::incident_edge_iterator incident = s.graph.incident_begin(s.c);
    CHECK((*incident++) == Edge(2, 0));
    CHECK((*incident--) == Edge(2, 1));

    Graph::adjacent_vertex_iterator adjacent = s.graph.adjacent_begin(s.c);
    CHECK_EQ((*adjacent++).id, 0u);
    CHECK_EQ((*adjacent--).id, 1u);
    CHECK_EQ((*adjacent).id, 0u);
}

TEST(iterators_walk_backwards_from_end)
{
    Sample s;
    Names backwards;
    Graph::vertex_iterator it = s.graph.vertices_end();
    while (it != s.graph.vertices_begin()) {
        --it;
        backwards.push_back((*it).value);
    }
    CHECK(backwards == (Names{"D", "C", "B", "A"}));
    CHECK(s.graph.edges_begin() != s.graph.edges_end());
    Graph::edge_iterator first = s.graph.edges_begin();
    --first;  // decrementing the first edge stays in place
    CHECK(first == s.graph.edges_begin());
}

TEST(mutable_iterator_converts_to_const_and_modifies_values)
{
    Sample s;
    Graph::vertex_iterator it = s.graph.vertices_begin();
    (*it).value = "Changed";
    Graph::const_vertex_iterator const_it = it;
    CHECK_EQ((*const_it).value, std::string("Changed"));
    Graph::const_edge_iterator const_edge = s.graph.edges_begin();
    CHECK((*const_edge) == Edge(0, 1));
    Graph::const_incident_edge_iterator const_incident = s.graph.incident_begin(s.c);
    CHECK((*const_incident) == Edge(2, 0));
    Graph::const_adjacent_vertex_iterator const_adjacent = s.graph.adjacent_begin(s.c);
    CHECK_EQ((*const_adjacent).value, std::string("Changed"));
    CHECK(Graph::vertex_iterator() == Graph::vertex_iterator());
}

TEST(erase_vertex_by_iterator)
{
    Sample s;
    Graph::vertex_iterator it = s.graph.vertices_begin();
    ++it;
    Graph::vertex_iterator next = s.graph.erase_vertex(it);
    CHECK_EQ((*next).value, std::string("C"));
    CHECK(!s.graph.contains_vertex(s.b));
    CHECK_EQ(s.graph.edge_count(), 2u);
}

TEST(erase_edge_by_iterator)
{
    Sample s;
    Graph::edge_iterator next = s.graph.erase_edge(s.graph.edges_begin());
    CHECK((*next) == Edge(0, 2));
    CHECK(!s.graph.contains_edge(s.a, s.b));
    CHECK_EQ(s.graph.edge_count(), 3u);
    Graph::edge_iterator last = --s.graph.edges_end();
    CHECK(s.graph.erase_edge(last) == s.graph.edges_end());
}

TEST(erase_by_iterator_rejects_foreign_and_end_iterators)
{
    Sample s;
    Graph other(s.graph);
    CHECK_THROWS(s.graph.erase_vertex(other.vertices_begin()), std::invalid_argument);
    CHECK_THROWS(s.graph.erase_edge(other.edges_begin()), std::invalid_argument);
    CHECK_THROWS(s.graph.erase_vertex(s.graph.vertices_end()), std::out_of_range);
    CHECK_THROWS(s.graph.erase_edge(s.graph.edges_end()), std::out_of_range);
    Graph::edge_iterator no_edge = s.graph.edges_begin();
    ++no_edge;
    ++no_edge;
    ++no_edge;
    ++no_edge;
    CHECK_THROWS(s.graph.erase_edge(no_edge), std::out_of_range);
}

TEST(equality_and_ordering_of_equal_graphs)
{
    Sample s;
    Graph copy(s.graph);
    CHECK(copy == s.graph);
    CHECK(!(copy != s.graph));
    CHECK(copy <= s.graph && copy >= s.graph);
    CHECK(!(copy < s.graph) && !(copy > s.graph));
}

TEST(ordering_by_counts_matrix_and_values)
{
    Sample s;
    Graph more_vertices(s.graph);
    more_vertices.add_vertex("E");
    Graph fewer_edges(s.graph);
    fewer_edges.remove_edge(0, 1);
    Graph other_value(s.graph);
    other_value.value(0) = "0";
    CHECK(more_vertices != s.graph && more_vertices > s.graph && s.graph < more_vertices);
    CHECK(fewer_edges != s.graph && fewer_edges < s.graph && s.graph >= fewer_edges);
    CHECK(other_value != s.graph && other_value < s.graph && s.graph > other_value);
}

TEST(ordering_same_edge_count_different_matrix)
{
    Graph first;
    Graph second;
    for (int i = 0; i < 3; ++i) {
        first.add_vertex("v");
        second.add_vertex("v");
    }
    first.add_edge(0, 1);
    second.add_edge(0, 2);
    CHECK(first > second && second < first && first != second);
}
