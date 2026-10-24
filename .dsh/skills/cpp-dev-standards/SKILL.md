---
name: cpp-dev-standards
description: C++ 开发规范（C++11 + VS2017 + GCC）。Use when writing, reviewing, or debugging any C++ code, CMakeLists, Makefiles, or VS2017 project files in this workspace. 覆盖总体要求与项目要求。
---

# C++ 开发规范（C++11 / VS2017 / GCC）

## 开发环境

| 项目 | 要求 |
|------|------|
| 语言标准 | **C++11**（禁止使用 C++14/17/20 特性） |
| Windows 编译器 | Visual Studio 2017（MSVC 19.1x，工具集 v141） |
| Linux 编译器 | GCC（4.8.5 及以上，需完整支持 C++11） |
| 构建系统 | CMake 3.10+ 或各平台原生工程 |
| 目标平台 | Windows x64、Linux x64 |

环境硬性约束（写任何代码前先读）：

- 代码必须同时在 **MSVC (VS2017)** 和 **GCC** 下无警告编译通过。
- MSVC 没有真正的 C++11 模式开关（`/std:c++11` 不存在；VS2017 只有 `/std:c++14`（默认）、`/std:c++17`、`/std:c++latest`）。因此 Windows 侧**保持默认开关，靠本规范的特性白名单约束代码只用 C++11**。
- 禁止使用任何编译器私有扩展；确需平台属性（如导出符号）必须用宏隔离成跨编译器写法。
- 源文件编码统一 **UTF-8（无 BOM）**（MSVC 侧如遇中文字符串乱码，用 `/utf-8` 编译选项解决）。

## 总体要求

1. **可移植性优先**：只用 C++11 标准特性和标准库。编译器扩展一律用宏隔离，示例：

   ```cpp
   #if defined(_MSC_VER)
   #  define MYAPP_EXPORT __declspec(dllexport)
   #elif defined(__GNUC__)
   #  define MYAPP_EXPORT __attribute__((visibility("default")))
   #endif
   ```

2. **双编译器零警告**：提交前分别在 VS2017（`/W4`）和 GCC（`-Wall -Wextra`）下编译，不得有新增警告。

3. **无未定义行为**：不读未初始化变量、不越界、不违反严格别名规则；有条件时用 ASan/UBSan（GCC）复查。

4. **命名规范**：

   | 对象 | 风格 | 示例 |
   |------|------|------|
   | 类/结构/枚举 | `PascalCase` | `HttpClient` |
   | 函数与变量 | `camelCase` | `sendRequest`、`retryCount` |
   | 宏 | `UPPER_SNAKE_CASE` + 项目前缀 | `MYAPP_LOG_INFO` |
   | 成员变量 | `m_` 前缀 | `m_endpoint` |
   | 静态/全局变量 | `s_` / `g_` 前缀 | `s_instance`、`g_config` |
   | 接口类（纯虚基类） | `I` 开头 | `ILogSink` |

5. **头文件**：

   - 每个头文件必须有 include guard 或 `#pragma once`（项目内统一一种）。
   - 头文件必须自包含：单独 include 也能编译通过。
   - 能前置声明就不 include；include 顺序：C 系统头 → C++ 标准库 → 第三方库 → 本项目头，组内字母序。
   - 禁止在头文件中写 `using namespace std;`。

6. **RAII 与资源管理**：

   - 堆资源用 `std::unique_ptr` / `std::shared_ptr`；业务代码禁止裸 `new`/`delete`。
   - 文件、锁、句柄等系统资源必须 RAII 封装。

7. **异常与错误处理**：

   - 对外接口优先错误码风格；若使用异常，必须保证基本异常安全，并明确标注 `noexcept` 与否。
   - 异常不得跨动态库（DLL/SO）边界传播（见项目要求第 7 条）。

8. **const 正确性**：入参尽量 `const T&` / `const T*`；查询类方法默认标 `const`。

9. **注释与文档**：对外头文件的接口必须有 Doxygen 风格注释（`///` 或 `/** */`），说明参数、返回值、使用前提。

10. **代码格式**：4 空格缩进（禁用 Tab）；单行 ≤ 120 列；K&R 大括号风格。

11. **提交自查**：`git diff` 确认无临时调试代码、无被注释掉的死代码。

## 项目要求

以下规则在总体要求之上，约束本工作区代码的组织与交付。

1. **目录结构**（新增 C++ 代码时固定落位）：

   ```
   ├─ src/                 # 源文件（.cpp）
   ├─ include/             # 对外头文件（.h）
   ├─ tests/               # 单元测试
   ├─ docs/                # 设计与接口文档
   ├─ third_party/         # 第三方依赖（如引入）
   ├─ build/               # 构建输出（不入库，进 .gitignore）
   ├─ CMakeLists.txt
   └─ Makefile             # Linux 备用构建脚本
   ```

2. **构建脚本规范**：

   - CMake 最低版本 3.10；设置 `CMAKE_CXX_STANDARD 11`、`CMAKE_CXX_STANDARD_REQUIRED ON`。
   - GCC 侧必须带 `-Wall -Wextra -std=c++11`。
   - MSVC 工程用平台工具集 `v141`；只保留 `x64` 配置，与 GCC 侧 x64 对齐；不提交 `*.vcxproj.user`。

3. **第三方依赖**：放入 `third_party/`，须同时给出 Windows 与 Linux 两种构建方式；禁止把外部源码直接复制进 `src/`。

4. **测试要求**：每个对外接口（include/ 下的类/函数）至少一条编译期实例化检查和一条运行期用例；测试不得依赖网络。

5. **接口文档同步**：`docs/` 内 API 说明必须与 include/ 接口一致；接口变更未同步文档视为不完整提交。

6. **跨编译器 ABI**：动态库对外导出一律 `extern "C"` 函数 + POD/standard-layout 结构体；**禁止跨 DLL 边界传递 `std::string`/`std::vector` 等 STL 类型**（MSVC 与 GCC 的 STL ABI 不兼容）。

7. **构建验证命令**（提交前必须双跑零警告）：

   - Linux / GCC：
     ```bash
     g++ -std=c++11 -Wall -Wextra -o build/app src/*.cpp
     ```
   - Windows / VS2017（在 “x64 Native Tools Command Prompt for VS 2017” 中）：
     ```bat
     cl /W4 /EHsc /utf-8 src\*.cpp /Fe:build\app.exe
     ```
     （不加 `/std` 开关，默认档位下仅使用 C++11 特性白名单内的语法。）

8. **提交检查清单**（提 PR 前逐项打勾）：

   - [ ] Windows VS2017 `/W4` 无警告
   - [ ] Linux GCC `-Wall -Wextra` 无警告
   - [ ] 新增头文件自包含、有 include guard
   - [ ] `.gitignore` 覆盖 `build/`、`*.user`、`*.VC.db`
   - [ ] 接口文档已同步
   - [ ] 无临时调试代码与死代码

## 使用步骤

1. 写/改任何 `.cpp`/`.h` 文件前，先重读“总体要求”的命名、头文件与 RAII 规则。
2. 新文件落位：源文件进 `src/`，对外头文件进 `include/`，文档进 `docs/`；临时实验代码放 `tests/`，不入 `src/`。
3. 按“项目要求”第 7 条命令双编译器验证，确保零警告。
4. 对外接口变更时同步更新 `docs/` 内 API 文档。
5. 提交前走完“提交检查清单”。

## 参考

- C++11 特性清单：https://en.cppreference.com/w/cpp/11
- GCC C++11 支持状态：https://gcc.gnu.org/projects/cxx-status.html
- MSVC 语言符合性：https://learn.microsoft.com/en-us/cpp/overview/visual-cpp-language-conformance
