# Lab 4 build: `make` builds the app, `make test` runs unit tests, `make coverage` checks >= 90 % line coverage,
# `make lint` runs cppcheck, `make docs` builds Doxygen documentation.
CXX      ?= g++
STD      := -std=c++17
WARNINGS := -Wall -Wextra -Wpedantic -Wshadow -Wconversion -Werror
INCLUDES := -Iinclude -Itests
BUILD    := build
COV      := $(BUILD)/coverage

APP_SOURCES  := src/menu.cpp src/main.cpp
TEST_SOURCES := src/menu.cpp tests/test_main.cpp tests/test_sorting.cpp tests/test_graph.cpp tests/test_menu.cpp
HEADERS      := $(wildcard include/lab4/*.hpp) $(wildcard tests/*.hpp)

.PHONY: all test coverage lint docs run clean

all: $(BUILD)/lab4

$(BUILD)/lab4: $(APP_SOURCES) $(HEADERS)
	@mkdir -p $(BUILD)
	$(CXX) $(STD) -O2 $(WARNINGS) $(INCLUDES) $(APP_SOURCES) -o $@

$(BUILD)/tests: $(TEST_SOURCES) $(HEADERS)
	@mkdir -p $(BUILD)
	$(CXX) $(STD) -O1 $(WARNINGS) $(INCLUDES) $(TEST_SOURCES) -o $@

run: $(BUILD)/lab4
	$(abspath $(BUILD))/lab4

test: $(BUILD)/tests
	$(abspath $(BUILD))/tests

coverage:
	@rm -rf $(COV) && mkdir -p $(COV)
	$(CXX) $(STD) -O0 --coverage $(INCLUDES) $(TEST_SOURCES) -o $(COV)/tests
	cd $(COV) && $(abspath $(COV))/tests
	python3 scripts/check_coverage.py $(COV) 90

lint:
	cppcheck --enable=warning,style,performance,portability --std=c++17 --error-exitcode=1 \
		--suppress=missingIncludeSystem --inline-suppr -Iinclude src include

docs:
	doxygen Doxyfile

clean:
	rm -rf $(BUILD) docs
