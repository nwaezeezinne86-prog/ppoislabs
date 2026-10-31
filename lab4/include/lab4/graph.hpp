/**
 * @file graph.hpp
 * @brief Generic undirected graph stored as an adjacency matrix.
 */
#ifndef LAB4_GRAPH_HPP
#define LAB4_GRAPH_HPP

#include <algorithm>
#include <cstddef>
#include <iterator>
#include <ostream>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <vector>

namespace lab4 {

/**
 * @brief Undirected simple graph (no loops, no parallel edges) stored as an adjacency matrix.
 *
 * The internal representation is private: users work with stable vertex identifiers, methods and iterators.
 * Iterators are bidirectional, come in mutable / const / reverse flavours and are invalidated by any
 * structural change of the graph (the erase_* methods return a valid iterator to the following element).
 *
 * @tparam T type of the value stored in a vertex.
 */
template <typename T>
class UndirectedGraph {
public:
    using value_type = T;                          ///< Type of the value stored in a vertex.
    using size_type = std::size_t;                 ///< Type of counts and degrees.
    using vertex_id = std::size_t;                 ///< Stable identifier of a vertex (never reused).
    using edge_type = std::pair<vertex_id, vertex_id>;  ///< Edge as a pair of vertex identifiers.

    /** @brief Reference to a vertex: its identifier plus a reference to the stored value. */
    template <bool IsConst>
    struct VertexRefT {
        vertex_id id;  ///< Vertex identifier.
        std::conditional_t<IsConst, const T&, T&> value;  ///< Stored value.
    };
    using vertex_ref = VertexRefT<false>;        ///< Mutable vertex reference.
    using const_vertex_ref = VertexRefT<true>;   ///< Read-only vertex reference.

    /** @brief Bidirectional iterator over vertices; dereferences to a VertexRefT. */
    template <bool IsConst>
    class VertexIteratorT {
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = VertexRefT<IsConst>;
        using difference_type = std::ptrdiff_t;
        using pointer = void;
        using reference = VertexRefT<IsConst>;

        VertexIteratorT() = default;

        /** @brief Converts a mutable iterator into a const one. */
        template <bool OtherConst, typename = std::enable_if_t<IsConst && !OtherConst>>
        VertexIteratorT(const VertexIteratorT<OtherConst>& other) : graph_(other.graph_), index_(other.index_)
        {
        }

        /** @brief Returns the current vertex (identifier and value reference). */
        reference operator*() const { return reference{graph_->ids_[index_], graph_->values_[index_]}; }
        /** @brief Moves to the next vertex. */
        VertexIteratorT& operator++() { ++index_; return *this; }
        /** @brief Moves to the next vertex, returns the old position. */
        VertexIteratorT operator++(int) { VertexIteratorT old = *this; ++index_; return old; }
        /** @brief Moves to the previous vertex. */
        VertexIteratorT& operator--() { --index_; return *this; }
        /** @brief Moves to the previous vertex, returns the old position. */
        VertexIteratorT operator--(int) { VertexIteratorT old = *this; --index_; return old; }
        /** @brief Equality of positions. */
        friend bool operator==(const VertexIteratorT& a, const VertexIteratorT& b)
        {
            return a.graph_ == b.graph_ && a.index_ == b.index_;
        }
        /** @brief Inequality of positions. */
        friend bool operator!=(const VertexIteratorT& a, const VertexIteratorT& b) { return !(a == b); }

    private:
        using GraphPtr = std::conditional_t<IsConst, const UndirectedGraph*, UndirectedGraph*>;
        friend class UndirectedGraph;
        friend class VertexIteratorT<!IsConst>;
        VertexIteratorT(GraphPtr graph, size_type index) : graph_(graph), index_(index) {}
        GraphPtr graph_ = nullptr;
        size_type index_ = 0;
    };

    /** @brief Bidirectional iterator over all edges; dereferences to an edge_type (by value). */
    template <bool IsConst>
    class EdgeIteratorT {
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = edge_type;
        using difference_type = std::ptrdiff_t;
        using pointer = void;
        using reference = edge_type;

        EdgeIteratorT() = default;

        /** @brief Converts a mutable iterator into a const one. */
        template <bool OtherConst, typename = std::enable_if_t<IsConst && !OtherConst>>
        EdgeIteratorT(const EdgeIteratorT<OtherConst>& other) : graph_(other.graph_), position_(other.position_)
        {
        }

        /** @brief Returns the current edge (smaller matrix index first). */
        reference operator*() const { return graph_->edge_at(position_); }
        /** @brief Moves to the next edge. */
        EdgeIteratorT& operator++() { position_ = graph_->next_edge(position_ + 1); return *this; }
        /** @brief Moves to the next edge, returns the old position. */
        EdgeIteratorT operator++(int) { EdgeIteratorT old = *this; ++*this; return old; }
        /** @brief Moves to the previous edge. */
        EdgeIteratorT& operator--() { position_ = graph_->previous_edge(position_); return *this; }
        /** @brief Moves to the previous edge, returns the old position. */
        EdgeIteratorT operator--(int) { EdgeIteratorT old = *this; --*this; return old; }
        /** @brief Equality of positions. */
        friend bool operator==(const EdgeIteratorT& a, const EdgeIteratorT& b)
        {
            return a.graph_ == b.graph_ && a.position_ == b.position_;
        }
        /** @brief Inequality of positions. */
        friend bool operator!=(const EdgeIteratorT& a, const EdgeIteratorT& b) { return !(a == b); }

    private:
        using GraphPtr = std::conditional_t<IsConst, const UndirectedGraph*, UndirectedGraph*>;
        friend class UndirectedGraph;
        friend class EdgeIteratorT<!IsConst>;
        EdgeIteratorT(GraphPtr graph, size_type position) : graph_(graph), position_(position) {}
        GraphPtr graph_ = nullptr;
        size_type position_ = 0;  // row * n + column of the upper-triangle cell, n * n means "end"
    };

    /** @brief Bidirectional iterator over the edges incident to one vertex (that vertex is `first`). */
    template <bool IsConst>
    class IncidentEdgeIteratorT {
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = edge_type;
        using difference_type = std::ptrdiff_t;
        using pointer = void;
        using reference = edge_type;

        IncidentEdgeIteratorT() = default;

        /** @brief Converts a mutable iterator into a const one. */
        template <bool OtherConst, typename = std::enable_if_t<IsConst && !OtherConst>>
        IncidentEdgeIteratorT(const IncidentEdgeIteratorT<OtherConst>& other)
            : graph_(other.graph_), row_(other.row_), column_(other.column_)
        {
        }

        /** @brief Returns the current edge as (base vertex, neighbour). */
        reference operator*() const { return edge_type(graph_->ids_[row_], graph_->ids_[column_]); }
        /** @brief Moves to the next incident edge. */
        IncidentEdgeIteratorT& operator++() { column_ = graph_->next_neighbour(row_, column_ + 1); return *this; }
        /** @brief Moves to the next incident edge, returns the old position. */
        IncidentEdgeIteratorT operator++(int) { IncidentEdgeIteratorT old = *this; ++*this; return old; }
        /** @brief Moves to the previous incident edge. */
        IncidentEdgeIteratorT& operator--() { column_ = graph_->previous_neighbour(row_, column_); return *this; }
        /** @brief Moves to the previous incident edge, returns the old position. */
        IncidentEdgeIteratorT operator--(int) { IncidentEdgeIteratorT old = *this; --*this; return old; }
        /** @brief Equality of positions. */
        friend bool operator==(const IncidentEdgeIteratorT& a, const IncidentEdgeIteratorT& b)
        {
            return a.graph_ == b.graph_ && a.row_ == b.row_ && a.column_ == b.column_;
        }
        /** @brief Inequality of positions. */
        friend bool operator!=(const IncidentEdgeIteratorT& a, const IncidentEdgeIteratorT& b) { return !(a == b); }

    private:
        using GraphPtr = std::conditional_t<IsConst, const UndirectedGraph*, UndirectedGraph*>;
        friend class UndirectedGraph;
        friend class IncidentEdgeIteratorT<!IsConst>;
        IncidentEdgeIteratorT(GraphPtr graph, size_type row, size_type column)
            : graph_(graph), row_(row), column_(column)
        {
        }
        GraphPtr graph_ = nullptr;
        size_type row_ = 0;
        size_type column_ = 0;
    };

    /** @brief Bidirectional iterator over the vertices adjacent to one vertex. */
    template <bool IsConst>
    class AdjacentVertexIteratorT {
    public:
        using iterator_category = std::bidirectional_iterator_tag;
        using value_type = VertexRefT<IsConst>;
        using difference_type = std::ptrdiff_t;
        using pointer = void;
        using reference = VertexRefT<IsConst>;

        AdjacentVertexIteratorT() = default;

        /** @brief Converts a mutable iterator into a const one. */
        template <bool OtherConst, typename = std::enable_if_t<IsConst && !OtherConst>>
        AdjacentVertexIteratorT(const AdjacentVertexIteratorT<OtherConst>& other)
            : graph_(other.graph_), row_(other.row_), column_(other.column_)
        {
        }

        /** @brief Returns the current neighbour (identifier and value reference). */
        reference operator*() const { return reference{graph_->ids_[column_], graph_->values_[column_]}; }
        /** @brief Moves to the next neighbour. */
        AdjacentVertexIteratorT& operator++() { column_ = graph_->next_neighbour(row_, column_ + 1); return *this; }
        /** @brief Moves to the next neighbour, returns the old position. */
        AdjacentVertexIteratorT operator++(int) { AdjacentVertexIteratorT old = *this; ++*this; return old; }
        /** @brief Moves to the previous neighbour. */
        AdjacentVertexIteratorT& operator--() { column_ = graph_->previous_neighbour(row_, column_); return *this; }
        /** @brief Moves to the previous neighbour, returns the old position. */
        AdjacentVertexIteratorT operator--(int) { AdjacentVertexIteratorT old = *this; --*this; return old; }
        /** @brief Equality of positions. */
        friend bool operator==(const AdjacentVertexIteratorT& a, const AdjacentVertexIteratorT& b)
        {
            return a.graph_ == b.graph_ && a.row_ == b.row_ && a.column_ == b.column_;
        }
        /** @brief Inequality of positions. */
        friend bool operator!=(const AdjacentVertexIteratorT& a, const AdjacentVertexIteratorT& b)
        {
            return !(a == b);
        }

    private:
        using GraphPtr = std::conditional_t<IsConst, const UndirectedGraph*, UndirectedGraph*>;
        friend class UndirectedGraph;
        friend class AdjacentVertexIteratorT<!IsConst>;
        AdjacentVertexIteratorT(GraphPtr graph, size_type row, size_type column)
            : graph_(graph), row_(row), column_(column)
        {
        }
        GraphPtr graph_ = nullptr;
        size_type row_ = 0;
        size_type column_ = 0;
    };

    using vertex_iterator = VertexIteratorT<false>;                     ///< Mutable vertex iterator.
    using const_vertex_iterator = VertexIteratorT<true>;                ///< Const vertex iterator.
    using reverse_vertex_iterator = std::reverse_iterator<vertex_iterator>;              ///< Reverse mutable.
    using const_reverse_vertex_iterator = std::reverse_iterator<const_vertex_iterator>;  ///< Reverse const.

    using edge_iterator = EdgeIteratorT<false>;                         ///< Mutable edge iterator.
    using const_edge_iterator = EdgeIteratorT<true>;                    ///< Const edge iterator.
    using reverse_edge_iterator = std::reverse_iterator<edge_iterator>;                  ///< Reverse mutable.
    using const_reverse_edge_iterator = std::reverse_iterator<const_edge_iterator>;      ///< Reverse const.

    using incident_edge_iterator = IncidentEdgeIteratorT<false>;        ///< Mutable incident-edge iterator.
    using const_incident_edge_iterator = IncidentEdgeIteratorT<true>;   ///< Const incident-edge iterator.
    using reverse_incident_edge_iterator = std::reverse_iterator<incident_edge_iterator>;  ///< Reverse mutable.
    using const_reverse_incident_edge_iterator = std::reverse_iterator<const_incident_edge_iterator>;  ///< Reverse const.

    using adjacent_vertex_iterator = AdjacentVertexIteratorT<false>;    ///< Mutable adjacent-vertex iterator.
    using const_adjacent_vertex_iterator = AdjacentVertexIteratorT<true>;  ///< Const adjacent-vertex iterator.
    using reverse_adjacent_vertex_iterator = std::reverse_iterator<adjacent_vertex_iterator>;  ///< Reverse mutable.
    using const_reverse_adjacent_vertex_iterator = std::reverse_iterator<const_adjacent_vertex_iterator>;  ///< Reverse const.

    // ---------- special members ----------

    /** @brief Creates an empty graph. */
    UndirectedGraph() = default;
    /** @brief Deep copy. */
    UndirectedGraph(const UndirectedGraph& other) = default;
    /** @brief Copy assignment (deep copy). */
    UndirectedGraph& operator=(const UndirectedGraph& other) = default;
    /** @brief Destructor; all memory is owned by std::vector members. */
    ~UndirectedGraph() = default;

    // ---------- size, clearing ----------

    /** @brief True when the graph has no vertices. */
    bool empty() const { return ids_.empty(); }
    /** @brief Number of vertices. */
    size_type vertex_count() const { return ids_.size(); }
    /** @brief Number of edges. */
    size_type edge_count() const { return edge_count_; }
    /** @brief Removes all vertices and edges (identifiers are not reused). */
    void clear()
    {
        ids_.clear();
        values_.clear();
        matrix_.clear();
        edge_count_ = 0;
    }

    // ---------- queries ----------

    /** @brief True when a vertex with this identifier exists. */
    bool contains_vertex(vertex_id id) const { return find_index(id) != ids_.size(); }

    /** @brief True when both vertices exist and are connected by an edge. */
    bool contains_edge(vertex_id first, vertex_id second) const
    {
        size_type i = find_index(first);
        size_type j = find_index(second);
        return i != ids_.size() && j != ids_.size() && matrix_[i][j] != 0;
    }

    /** @brief Number of edges incident to the vertex. @throws std::out_of_range if the vertex is unknown. */
    size_type vertex_degree(vertex_id id) const { return degree_at(index_of(id)); }

    /**
     * @brief Degree of an edge: number of other edges sharing an end with it, deg(u) + deg(v) - 2.
     * @throws std::out_of_range if a vertex or the edge does not exist.
     */
    size_type edge_degree(vertex_id first, vertex_id second) const
    {
        size_type i = index_of(first);
        size_type j = index_of(second);
        if (matrix_[i][j] == 0) {
            throw std::out_of_range("edge not found");
        }
        return degree_at(i) + degree_at(j) - 2;
    }

    /** @brief Value stored in a vertex. @throws std::out_of_range if the vertex is unknown. */
    T& value(vertex_id id) { return values_[index_of(id)]; }
    /** @brief Read-only value stored in a vertex. @throws std::out_of_range if the vertex is unknown. */
    const T& value(vertex_id id) const { return values_[index_of(id)]; }

    // ---------- modification ----------

    /** @brief Adds a vertex holding @p value and returns its new identifier. */
    vertex_id add_vertex(const T& value)
    {
        size_type count = ids_.size();
        for (Row& row : matrix_) {
            row.push_back(0);
        }
        matrix_.push_back(Row(count + 1, 0));
        ids_.push_back(next_id_);
        values_.push_back(value);
        return next_id_++;
    }

    /**
     * @brief Adds an undirected edge.
     * @throws std::out_of_range if a vertex is unknown.
     * @throws std::invalid_argument for a loop or an already existing edge.
     */
    void add_edge(vertex_id first, vertex_id second)
    {
        size_type i = index_of(first);
        size_type j = index_of(second);
        if (i == j) {
            throw std::invalid_argument("loops are not supported");
        }
        if (matrix_[i][j] != 0) {
            throw std::invalid_argument("edge already exists");
        }
        set_edge(i, j, 1);
        ++edge_count_;
    }

    /** @brief Removes a vertex with all incident edges. @throws std::out_of_range if the vertex is unknown. */
    void remove_vertex(vertex_id id) { erase_at(index_of(id)); }

    /** @brief Removes an edge. @throws std::out_of_range if a vertex or the edge does not exist. */
    void remove_edge(vertex_id first, vertex_id second)
    {
        size_type i = index_of(first);
        size_type j = index_of(second);
        if (matrix_[i][j] == 0) {
            throw std::out_of_range("edge not found");
        }
        set_edge(i, j, 0);
        --edge_count_;
    }

    /**
     * @brief Removes the vertex the iterator points at.
     * @return iterator to the vertex that followed the removed one; all other iterators become invalid.
     * @throws std::invalid_argument if the iterator belongs to another graph.
     * @throws std::out_of_range if the iterator does not point at a vertex.
     */
    vertex_iterator erase_vertex(vertex_iterator position)
    {
        require_owner(position.graph_);
        if (position.index_ >= ids_.size()) {
            throw std::out_of_range("iterator does not point at a vertex");
        }
        erase_at(position.index_);
        return vertex_iterator(this, position.index_);
    }

    /**
     * @brief Removes the edge the iterator points at.
     * @return iterator to the edge that followed the removed one; all other iterators become invalid.
     * @throws std::invalid_argument if the iterator belongs to another graph.
     * @throws std::out_of_range if the iterator does not point at an edge.
     */
    edge_iterator erase_edge(edge_iterator position)
    {
        require_owner(position.graph_);
        size_type size = ids_.size();
        if (position.position_ >= size * size || !is_edge_cell(position.position_)) {
            throw std::out_of_range("iterator does not point at an edge");
        }
        set_edge(position.position_ / size, position.position_ % size, 0);
        --edge_count_;
        return edge_iterator(this, next_edge(position.position_ + 1));
    }

    // ---------- iterators over vertices ----------

    /** @brief Iterator to the first vertex. */
    vertex_iterator vertices_begin() { return vertex_iterator(this, 0); }
    /** @brief Iterator past the last vertex. */
    vertex_iterator vertices_end() { return vertex_iterator(this, ids_.size()); }
    /** @brief Const iterator to the first vertex. */
    const_vertex_iterator vertices_begin() const { return const_vertex_iterator(this, 0); }
    /** @brief Const iterator past the last vertex. */
    const_vertex_iterator vertices_end() const { return const_vertex_iterator(this, ids_.size()); }
    /** @brief Const iterator to the first vertex. */
    const_vertex_iterator vertices_cbegin() const { return vertices_begin(); }
    /** @brief Const iterator past the last vertex. */
    const_vertex_iterator vertices_cend() const { return vertices_end(); }
    /** @brief Reverse iterator to the last vertex. */
    reverse_vertex_iterator vertices_rbegin() { return reverse_vertex_iterator(vertices_end()); }
    /** @brief Reverse iterator past the first vertex. */
    reverse_vertex_iterator vertices_rend() { return reverse_vertex_iterator(vertices_begin()); }
    /** @brief Const reverse iterator to the last vertex. */
    const_reverse_vertex_iterator vertices_rbegin() const { return const_reverse_vertex_iterator(vertices_end()); }
    /** @brief Const reverse iterator past the first vertex. */
    const_reverse_vertex_iterator vertices_rend() const { return const_reverse_vertex_iterator(vertices_begin()); }
    /** @brief Const reverse iterator to the last vertex. */
    const_reverse_vertex_iterator vertices_crbegin() const { return vertices_rbegin(); }
    /** @brief Const reverse iterator past the first vertex. */
    const_reverse_vertex_iterator vertices_crend() const { return vertices_rend(); }

    // ---------- iterators over edges ----------

    /** @brief Iterator to the first edge. */
    edge_iterator edges_begin() { return edge_iterator(this, next_edge(0)); }
    /** @brief Iterator past the last edge. */
    edge_iterator edges_end() { return edge_iterator(this, ids_.size() * ids_.size()); }
    /** @brief Const iterator to the first edge. */
    const_edge_iterator edges_begin() const { return const_edge_iterator(this, next_edge(0)); }
    /** @brief Const iterator past the last edge. */
    const_edge_iterator edges_end() const { return const_edge_iterator(this, ids_.size() * ids_.size()); }
    /** @brief Const iterator to the first edge. */
    const_edge_iterator edges_cbegin() const { return edges_begin(); }
    /** @brief Const iterator past the last edge. */
    const_edge_iterator edges_cend() const { return edges_end(); }
    /** @brief Reverse iterator to the last edge. */
    reverse_edge_iterator edges_rbegin() { return reverse_edge_iterator(edges_end()); }
    /** @brief Reverse iterator past the first edge. */
    reverse_edge_iterator edges_rend() { return reverse_edge_iterator(edges_begin()); }
    /** @brief Const reverse iterator to the last edge. */
    const_reverse_edge_iterator edges_rbegin() const { return const_reverse_edge_iterator(edges_end()); }
    /** @brief Const reverse iterator past the first edge. */
    const_reverse_edge_iterator edges_rend() const { return const_reverse_edge_iterator(edges_begin()); }
    /** @brief Const reverse iterator to the last edge. */
    const_reverse_edge_iterator edges_crbegin() const { return edges_rbegin(); }
    /** @brief Const reverse iterator past the first edge. */
    const_reverse_edge_iterator edges_crend() const { return edges_rend(); }

    // ---------- iterators over edges incident to a vertex ----------

    /** @brief Iterator to the first edge incident to the vertex. @throws std::out_of_range if unknown. */
    incident_edge_iterator incident_begin(vertex_id id)
    {
        size_type row = index_of(id);
        return incident_edge_iterator(this, row, next_neighbour(row, 0));
    }
    /** @brief Iterator past the last edge incident to the vertex. @throws std::out_of_range if unknown. */
    incident_edge_iterator incident_end(vertex_id id)
    {
        return incident_edge_iterator(this, index_of(id), ids_.size());
    }
    /** @brief Const iterator to the first incident edge. @throws std::out_of_range if unknown. */
    const_incident_edge_iterator incident_begin(vertex_id id) const
    {
        size_type row = index_of(id);
        return const_incident_edge_iterator(this, row, next_neighbour(row, 0));
    }
    /** @brief Const iterator past the last incident edge. @throws std::out_of_range if unknown. */
    const_incident_edge_iterator incident_end(vertex_id id) const
    {
        return const_incident_edge_iterator(this, index_of(id), ids_.size());
    }
    /** @brief Const iterator to the first incident edge. */
    const_incident_edge_iterator incident_cbegin(vertex_id id) const { return incident_begin(id); }
    /** @brief Const iterator past the last incident edge. */
    const_incident_edge_iterator incident_cend(vertex_id id) const { return incident_end(id); }
    /** @brief Reverse iterator to the last incident edge. */
    reverse_incident_edge_iterator incident_rbegin(vertex_id id)
    {
        return reverse_incident_edge_iterator(incident_end(id));
    }
    /** @brief Reverse iterator past the first incident edge. */
    reverse_incident_edge_iterator incident_rend(vertex_id id)
    {
        return reverse_incident_edge_iterator(incident_begin(id));
    }
    /** @brief Const reverse iterator to the last incident edge. */
    const_reverse_incident_edge_iterator incident_rbegin(vertex_id id) const
    {
        return const_reverse_incident_edge_iterator(incident_end(id));
    }
    /** @brief Const reverse iterator past the first incident edge. */
    const_reverse_incident_edge_iterator incident_rend(vertex_id id) const
    {
        return const_reverse_incident_edge_iterator(incident_begin(id));
    }
    /** @brief Const reverse iterator to the last incident edge. */
    const_reverse_incident_edge_iterator incident_crbegin(vertex_id id) const { return incident_rbegin(id); }
    /** @brief Const reverse iterator past the first incident edge. */
    const_reverse_incident_edge_iterator incident_crend(vertex_id id) const { return incident_rend(id); }

    // ---------- iterators over vertices adjacent to a vertex ----------

    /** @brief Iterator to the first neighbour of the vertex. @throws std::out_of_range if unknown. */
    adjacent_vertex_iterator adjacent_begin(vertex_id id)
    {
        size_type row = index_of(id);
        return adjacent_vertex_iterator(this, row, next_neighbour(row, 0));
    }
    /** @brief Iterator past the last neighbour of the vertex. @throws std::out_of_range if unknown. */
    adjacent_vertex_iterator adjacent_end(vertex_id id)
    {
        return adjacent_vertex_iterator(this, index_of(id), ids_.size());
    }
    /** @brief Const iterator to the first neighbour. @throws std::out_of_range if unknown. */
    const_adjacent_vertex_iterator adjacent_begin(vertex_id id) const
    {
        size_type row = index_of(id);
        return const_adjacent_vertex_iterator(this, row, next_neighbour(row, 0));
    }
    /** @brief Const iterator past the last neighbour. @throws std::out_of_range if unknown. */
    const_adjacent_vertex_iterator adjacent_end(vertex_id id) const
    {
        return const_adjacent_vertex_iterator(this, index_of(id), ids_.size());
    }
    /** @brief Const iterator to the first neighbour. */
    const_adjacent_vertex_iterator adjacent_cbegin(vertex_id id) const { return adjacent_begin(id); }
    /** @brief Const iterator past the last neighbour. */
    const_adjacent_vertex_iterator adjacent_cend(vertex_id id) const { return adjacent_end(id); }
    /** @brief Reverse iterator to the last neighbour. */
    reverse_adjacent_vertex_iterator adjacent_rbegin(vertex_id id)
    {
        return reverse_adjacent_vertex_iterator(adjacent_end(id));
    }
    /** @brief Reverse iterator past the first neighbour. */
    reverse_adjacent_vertex_iterator adjacent_rend(vertex_id id)
    {
        return reverse_adjacent_vertex_iterator(adjacent_begin(id));
    }
    /** @brief Const reverse iterator to the last neighbour. */
    const_reverse_adjacent_vertex_iterator adjacent_rbegin(vertex_id id) const
    {
        return const_reverse_adjacent_vertex_iterator(adjacent_end(id));
    }
    /** @brief Const reverse iterator past the first neighbour. */
    const_reverse_adjacent_vertex_iterator adjacent_rend(vertex_id id) const
    {
        return const_reverse_adjacent_vertex_iterator(adjacent_begin(id));
    }
    /** @brief Const reverse iterator to the last neighbour. */
    const_reverse_adjacent_vertex_iterator adjacent_crbegin(vertex_id id) const { return adjacent_rbegin(id); }
    /** @brief Const reverse iterator past the first neighbour. */
    const_reverse_adjacent_vertex_iterator adjacent_crend(vertex_id id) const { return adjacent_rend(id); }

    // ---------- comparison ----------

    /** @brief Equal when adjacency matrices and vertex values are equal (identifiers are ignored). */
    friend bool operator==(const UndirectedGraph& left, const UndirectedGraph& right)
    {
        return left.matrix_ == right.matrix_ && left.values_ == right.values_;
    }
    /** @brief Negation of operator==. */
    friend bool operator!=(const UndirectedGraph& left, const UndirectedGraph& right) { return !(left == right); }
    /** @brief Order: vertex count, edge count, matrix (row by row), vertex values. */
    friend bool operator<(const UndirectedGraph& left, const UndirectedGraph& right) { return compare(left, right) < 0; }
    /** @brief Greater-than, see operator<. */
    friend bool operator>(const UndirectedGraph& left, const UndirectedGraph& right) { return compare(left, right) > 0; }
    /** @brief Less-or-equal, see operator<. */
    friend bool operator<=(const UndirectedGraph& left, const UndirectedGraph& right) { return compare(left, right) <= 0; }
    /** @brief Greater-or-equal, see operator<. */
    friend bool operator>=(const UndirectedGraph& left, const UndirectedGraph& right) { return compare(left, right) >= 0; }

    /**
     * @brief Prints `Graph(V=.., E=..) vertices: [id:value, ..] edges: [a-b, ..]` using iterators and std::for_each.
     *
     * Requires `operator<<` for T.
     */
    friend std::ostream& operator<<(std::ostream& out, const UndirectedGraph& graph)
    {
        out << "Graph(V=" << graph.vertex_count() << ", E=" << graph.edge_count() << ") vertices: [";
        bool first = true;
        std::for_each(graph.vertices_begin(), graph.vertices_end(), [&](const_vertex_ref vertex) {
            out << (first ? "" : ", ") << vertex.id << ':' << vertex.value;
            first = false;
        });
        out << "] edges: [";
        first = true;
        std::for_each(graph.edges_begin(), graph.edges_end(), [&](const edge_type& edge) {
            out << (first ? "" : ", ") << edge.first << '-' << edge.second;
            first = false;
        });
        return out << ']';
    }

private:
    using Row = std::vector<unsigned char>;
    using Matrix = std::vector<Row>;

    std::vector<vertex_id> ids_;  // ascending, so lookups are binary searches
    std::vector<T> values_;
    Matrix matrix_;
    vertex_id next_id_ = 0;
    size_type edge_count_ = 0;

    static int compare(const UndirectedGraph& left, const UndirectedGraph& right)
    {
        if (left.ids_.size() != right.ids_.size()) {
            return left.ids_.size() < right.ids_.size() ? -1 : 1;
        }
        if (left.edge_count_ != right.edge_count_) {
            return left.edge_count_ < right.edge_count_ ? -1 : 1;
        }
        if (left.matrix_ != right.matrix_) {
            return left.matrix_ < right.matrix_ ? -1 : 1;
        }
        if (left.values_ == right.values_) {
            return 0;
        }
        return left.values_ < right.values_ ? -1 : 1;
    }

    size_type find_index(vertex_id id) const
    {
        auto found = std::lower_bound(ids_.begin(), ids_.end(), id);
        return (found != ids_.end() && *found == id) ? static_cast<size_type>(found - ids_.begin()) : ids_.size();
    }

    size_type index_of(vertex_id id) const
    {
        size_type index = find_index(id);
        if (index == ids_.size()) {
            throw std::out_of_range("vertex not found");
        }
        return index;
    }

    size_type degree_at(size_type index) const
    {
        return static_cast<size_type>(std::count(matrix_[index].begin(), matrix_[index].end(), 1));
    }

    void set_edge(size_type i, size_type j, unsigned char present)
    {
        matrix_[i][j] = present;
        matrix_[j][i] = present;
    }

    void erase_at(size_type index)
    {
        edge_count_ -= degree_at(index);
        matrix_.erase(matrix_.begin() + static_cast<std::ptrdiff_t>(index));
        for (Row& row : matrix_) {
            row.erase(row.begin() + static_cast<std::ptrdiff_t>(index));
        }
        ids_.erase(ids_.begin() + static_cast<std::ptrdiff_t>(index));
        values_.erase(values_.begin() + static_cast<std::ptrdiff_t>(index));
    }

    void require_owner(const UndirectedGraph* owner) const
    {
        if (owner != this) {
            throw std::invalid_argument("iterator belongs to another graph");
        }
    }

    // First column >= from in the row that holds an edge, or n when there is none.
    size_type next_neighbour(size_type row, size_type from) const
    {
        for (size_type column = from; column < ids_.size(); ++column) {
            if (matrix_[row][column] != 0) {
                return column;
            }
        }
        return ids_.size();
    }

    // Last column < from in the row that holds an edge; `from` itself when there is none.
    size_type previous_neighbour(size_type row, size_type from) const
    {
        for (size_type column = from; column > 0; --column) {
            if (matrix_[row][column - 1] != 0) {
                return column - 1;
            }
        }
        return from;
    }

    // Edge cells are the cells above the diagonal; position = row * n + column.
    bool is_edge_cell(size_type position) const
    {
        size_type size = ids_.size();
        size_type row = position / size;
        size_type column = position % size;
        return row < column && matrix_[row][column] != 0;
    }

    size_type next_edge(size_type from) const
    {
        size_type limit = ids_.size() * ids_.size();
        for (size_type position = from; position < limit; ++position) {
            if (is_edge_cell(position)) {
                return position;
            }
        }
        return limit;
    }

    size_type previous_edge(size_type from) const
    {
        for (size_type position = from; position > 0; --position) {
            if (is_edge_cell(position - 1)) {
                return position - 1;
            }
        }
        return from;
    }

    edge_type edge_at(size_type position) const
    {
        size_type size = ids_.size();
        return edge_type(ids_[position / size], ids_[position % size]);
    }
};

}  // namespace lab4

#endif  // LAB4_GRAPH_HPP
