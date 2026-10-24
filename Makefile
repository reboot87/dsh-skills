# Linux/GCC 备用构建脚本（skill 项目要求第 2、7 条）
# 用法：
#   make          # 构建库、demo、测试
#   make test     # 运行测试
#   make clean    # 清理构建输出

CXX      ?= g++
CXXFLAGS := -std=c++11 -Wall -Wextra -Iinclude
BUILD    := build

SRCS_LIB := src/ring_buffer.cpp
SRCS_APP := src/main.cpp
SRCS_TEST := tests/test_ring_buffer.cpp

.PHONY: all test clean

all: $(BUILD)/libfreemodel_core.a $(BUILD)/freemodel_demo $(BUILD)/test_ring_buffer

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/libfreemodel_core.a: $(SRCS_LIB) | $(BUILD)
	$(CXX) $(CXXFLAGS) -c $(SRCS_LIB) -o $(BUILD)/ring_buffer.o
	ar rcs $@ $(BUILD)/ring_buffer.o

$(BUILD)/freemodel_demo: $(SRCS_APP) $(BUILD)/libfreemodel_core.a
	$(CXX) $(CXXFLAGS) $(SRCS_APP) $(BUILD)/libfreemodel_core.a -o $@

$(BUILD)/test_ring_buffer: $(SRCS_TEST) $(BUILD)/libfreemodel_core.a
	$(CXX) $(CXXFLAGS) $(SRCS_TEST) $(BUILD)/libfreemodel_core.a -o $@

test: $(BUILD)/test_ring_buffer
	$(BUILD)/test_ring_buffer

clean:
	rm -rf $(BUILD)
