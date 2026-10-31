/**
 * @file sorting.hpp
 * @brief Generic sorting algorithms: bubble sort and patience sorting.
 *
 * Every algorithm is available in two forms:
 *  - an iterator-range form `f(first, last, comp)` (works with raw pointers, std::vector, std::list ...);
 *  - a container form `f(range, comp)` (works with C arrays and any container with begin()/end()).
 */
#ifndef LAB4_SORTING_HPP
#define LAB4_SORTING_HPP

#include <algorithm>
#include <cstddef>
#include <functional>
#include <iterator>
#include <queue>
#include <utility>
#include <vector>

namespace lab4 {

/**
 * @brief Bubble sort with the "last swap" optimisation.
 *
 * Stable. O(n^2) comparisons in the worst case, O(n) on sorted input, O(1) extra memory.
 *
 * @tparam ForwardIt forward iterator over a modifiable range.
 * @tparam Compare   strict weak ordering, `comp(a, b)` is true when `a` must precede `b`.
 * @param first beginning of the range.
 * @param last  end of the range.
 * @param comp  comparison function object (defaults to `std::less<>`).
 */
template <typename ForwardIt, typename Compare = std::less<>>
void bubble_sort(ForwardIt first, ForwardIt last, Compare comp = Compare())
{
    ForwardIt unsorted_end = last;
    while (first != unsorted_end) {
        ForwardIt last_swap = first;
        ForwardIt current = first;
        ForwardIt next = std::next(current);
        while (next != unsorted_end) {
            if (comp(*next, *current)) {
                std::iter_swap(current, next);
                last_swap = next;
            }
            current = next;
            ++next;
        }
        unsorted_end = last_swap;
    }
}

namespace detail {

/** @brief Finds the leftmost pile whose top is not smaller than @p item (piles' tops are increasing). */
template <typename Piles, typename Value, typename Compare>
typename Piles::iterator find_pile(Piles& piles, const Value& item, Compare comp)
{
    auto top_is_smaller = [&comp](const typename Piles::value_type& pile, const Value& value) {
        return comp(pile.back(), value);
    };
    return std::lower_bound(piles.begin(), piles.end(), item, top_is_smaller);
}

/** @brief Deals the range onto piles; every pile is non-increasing from bottom to top. */
template <typename Value, typename ForwardIt, typename Compare>
std::vector<std::vector<Value>> deal_piles(ForwardIt first, ForwardIt last, Compare comp)
{
    std::vector<std::vector<Value>> piles;
    for (; first != last; ++first) {
        auto pile = find_pile(piles, *first, comp);
        if (pile == piles.end()) {
            pile = piles.insert(piles.end(), std::vector<Value>());
        }
        pile->push_back(*first);
    }
    return piles;
}

/** @brief k-way merge of the piles back into the output range using a priority queue of pile tops. */
template <typename Value, typename OutputIt, typename Compare>
void merge_piles(std::vector<std::vector<Value>>& piles, OutputIt out, Compare comp)
{
    auto top_is_later = [&piles, &comp](std::size_t left, std::size_t right) {
        return comp(piles[right].back(), piles[left].back());
    };
    std::priority_queue<std::size_t, std::vector<std::size_t>, decltype(top_is_later)> heap(top_is_later);
    for (std::size_t index = 0; index < piles.size(); ++index) {
        heap.push(index);
    }
    while (!heap.empty()) {
        std::size_t smallest = heap.top();
        heap.pop();
        std::vector<Value>& pile = piles[smallest];
        *out = std::move(pile.back());
        ++out;
        pile.pop_back();
        if (!pile.empty()) {
            heap.push(smallest);
        }
    }
}

}  // namespace detail

/**
 * @brief Patience sorting.
 *
 * Items are dealt onto piles (binary search for the leftmost pile whose top is not smaller than the item),
 * then the piles are merged with a priority queue. O(n log n) time, O(n) extra memory, not stable.
 *
 * @tparam ForwardIt forward iterator over a modifiable range.
 * @tparam Compare   strict weak ordering.
 * @param first beginning of the range.
 * @param last  end of the range.
 * @param comp  comparison function object (defaults to `std::less<>`).
 */
template <typename ForwardIt, typename Compare = std::less<>>
void patience_sort(ForwardIt first, ForwardIt last, Compare comp = Compare())
{
    using Value = typename std::iterator_traits<ForwardIt>::value_type;
    std::vector<std::vector<Value>> piles = detail::deal_piles<Value>(first, last, comp);
    detail::merge_piles(piles, first, comp);
}

/** @brief Container form of bubble_sort(): sorts a C array or any container with begin()/end(). */
template <typename Range, typename Compare = std::less<>>
auto bubble_sort(Range& range, Compare comp = Compare()) -> decltype(std::begin(range), void())
{
    bubble_sort(std::begin(range), std::end(range), comp);
}

/** @brief Container form of patience_sort(): sorts a C array or any container with begin()/end(). */
template <typename Range, typename Compare = std::less<>>
auto patience_sort(Range& range, Compare comp = Compare()) -> decltype(std::begin(range), void())
{
    patience_sort(std::begin(range), std::end(range), comp);
}

}  // namespace lab4

#endif  // LAB4_SORTING_HPP
