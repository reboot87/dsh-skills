# RingBuffer 接口文档

> 生成依据：`include/freemodel/ring_buffer.h`（接口变更必须同步本文件 —— skill 项目要求第 5 条）。

## 概述

`freemodel::RingBuffer<T>` 是固定容量的环形缓冲区（FIFO 队列）。容量在构造时确定，不做动态扩容；缓冲区满时 `push` 覆盖最旧元素。

- **头文件**：`include/freemodel/ring_buffer.h`
- **实现**：`src/ring_buffer.cpp`（模板显式实例化）
- **命名空间**：`freemodel`
- **语言标准**：C++11，兼容 MSVC (VS2017, v141) 与 GCC 4.8.5+

## 已实例化类型

以下元素类型已在 `src/ring_buffer.cpp` 显式实例化并随库导出：

| 类型 | 状态 |
|------|------|
| `RingBuffer<int>` | 已导出 |
| `RingBuffer<double>` | 已导出 |

新增元素类型需在 `src/ring_buffer.cpp` 追加 `template class RingBuffer<T>;` 并更新本表。

## 接口清单

### 构造与析构

| 接口 | 说明 |
|------|------|
| `explicit RingBuffer(std::size_t capacity)` | 构造容量为 `capacity` 的空缓冲区；`capacity` 必须大于 0 |
| `~RingBuffer() noexcept` | 析构所有活跃元素并释放存储 |
| `RingBuffer(const RingBuffer&) = delete` | 禁止拷贝 |
| `RingBuffer& operator=(const RingBuffer&) = delete` | 禁止拷贝赋值 |
| `RingBuffer(RingBuffer&& other) noexcept` | 移动构造，接管 `other` 的存储；`other` 移动后为空 |
| `RingBuffer& operator=(RingBuffer&& other) noexcept` | 移动赋值；自赋值安全；`other` 移动后为空 |

### 数据操作

| 接口 | 返回 | 说明 |
|------|------|------|
| `bool push(const T& value) noexcept` | 是否发生覆盖 | 压入队尾；缓冲区满时丢弃最旧元素并返回 `true` |
| `bool pop(T* out) noexcept` | 是否成功 | 弹出队头写入 `*out`；空时返回 `false` 且不写 `out`。`out` 不可为 null |

### 查询

| 接口 | 返回 | 说明 |
|------|------|------|
| `std::size_t size() const noexcept` | 元素个数 | — |
| `std::size_t capacity() const noexcept` | 固定容量 | 构造时确定 |
| `bool isEmpty() const noexcept` | 是否为空 | — |

## 语义与保证

1. **异常安全**：所有成员函数 `noexcept`。要求元素类型 `T` 的拷贝构造与析构不抛出异常。
2. **线程安全**：本类不自带同步；并发访问需外部加锁。
3. **存储模型**：内部用 `operator new` 分配原始内存，槽位在 `push` 时 placement new 构造、`pop` 时显式析构；未使用槽位不持有活跃对象。因此 `T` 无需默认构造即可使用本容器。
4. **未定义行为边界**：`pop(nullptr)`、`capacity == 0` 为未定义行为。

## 使用示例

```cpp
#include "freemodel/ring_buffer.h"

freemodel::RingBuffer<int> buffer(3);
buffer.push(1);
buffer.push(2);
buffer.push(3);
buffer.push(4);              // 覆盖 1，缓冲区内容为 2 3 4

int value = 0;
while (buffer.pop(&value)) {
    // 依次得到 2、3、4
}
```

## 测试

`tests/test_ring_buffer.cpp` 覆盖：基础 push/pop、满覆盖、移动语义、多轮环绕下标回绕、编译期契约（`static_assert` 检查不可拷贝/可移动等）。

## 验证命令

- Linux/GCC：`g++ -std=c++11 -Wall -Wextra -Iinclude src/*.cpp -o build/app`
- Windows/VS2017：`cl /W4 /EHsc /utf-8 /Iinclude src\*.cpp /Fe:build\app.exe`
