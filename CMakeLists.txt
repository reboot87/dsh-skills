# C++11 / VS2017 (v141) / GCC 双平台构建脚本
# 规则来源：.dsh/skills/cpp-dev-standards/SKILL.md（项目要求第 2 条）

cmake_minimum_required(VERSION 3.10)

project(freemodel CXX)

# C++11 强制开启，不允许编译器降级到更低标准。
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 与目标平台对齐：只保留 x64 语义（MSVC 侧在生成器里选 x64 平台）。
if(CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(FATAL_ERROR "This project targets x64 only (project requirement #2).")
endif()

# ---------------------------------------------------------------------------
# 库目标：环形缓冲区实现（模板，头文件为主 + 显式实例化）。
# ---------------------------------------------------------------------------
add_library(freemodel_core STATIC
    src/ring_buffer.cpp
)
target_include_directories(freemodel_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

# GCC/Clang 侧零警告基线（skill 总体要求第 2 条）。
target_compile_options(freemodel_core PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-Wall -Wextra>
)

# MSVC 侧零警告基线；/utf-8 保证 UTF-8 源码内中文注释与字符串正确处理。
target_compile_options(freemodel_core PRIVATE
    $<$<CXX_COMPILER_ID:MSVC>:/W4 /utf-8>
)

# ---------------------------------------------------------------------------
# 演示程序。
# ---------------------------------------------------------------------------
add_executable(freemodel_demo
    src/main.cpp
)
target_link_libraries(freemodel_demo PRIVATE freemodel_core)

# ---------------------------------------------------------------------------
# 测试：不依赖网络与第三方测试框架（skill 项目要求第 4 条）。
# ---------------------------------------------------------------------------
add_executable(test_ring_buffer
    tests/test_ring_buffer.cpp
)
target_link_libraries(test_ring_buffer PRIVATE freemodel_core)
enable_testing()
add_test(NAME ring_buffer COMMAND test_ring_buffer)
