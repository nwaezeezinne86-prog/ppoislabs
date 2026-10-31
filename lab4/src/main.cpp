/** @file main.cpp
 *  @brief Entry point of the lab 4 console application. */
#include <iostream>

#include "lab4/menu.hpp"

/** @brief Starts the interactive menu on the standard streams. */
int main()
{
    lab4::Menu menu(std::cin, std::cout);
    menu.run();
    return 0;
}
