#pragma once

#include <cstddef>

namespace freemodel {

/// 固定容量的环形缓冲区（FIFO 队列）。
///
/// 线程安全性：本类不自带同步，多线程访问需外部加锁。
/// 异常安全性：所有方法均不抛出异常（元素类型 T 的大小版本除外，
/// 见 size() 的说明）。容量在构造时固定，不做动态扩容。
///
/// 典型用途：日志队列、生产者-消费者缓冲、限流窗口。
///
/// @tparam T 元素类型，要求可平凡复制（配合容器内部 placement 存储）
template <typename T>
class RingBuffer {
public:
    /// 构造一个容量为 capacity 的空缓冲区。
    ///
    /// @param capacity 最大容量，必须大于 0；否则行为未定义
    explicit RingBuffer(std::size_t capacity);

    /// 析构函数。
    ~RingBuffer() noexcept;

    /// 禁止拷贝（内部含裸资源，语义上共享缓冲区易出错）。
    RingBuffer(const RingBuffer&) = delete;
    /// 禁止拷贝赋值。
    RingBuffer& operator=(const RingBuffer&) = delete;

    /// 移动构造：接管 other 的内部存储。
    ///
    /// @param other 被移动的缓冲区，移动后处于有效但未定义状态
    RingBuffer(RingBuffer&& other) noexcept;

    /// 移动赋值：释放自身资源并接管 other。
    ///
    /// @param other 被移动的缓冲区，移动后处于有效但未定义状态
    /// @return 自身引用
    RingBuffer& operator=(RingBuffer&& other) noexcept;

    /// 向队尾压入一个元素。
    ///
    /// 缓冲区已满时丢弃最旧的元素（覆盖写）。
    ///
    /// @param value 待压入的元素
    /// @return 若因缓冲区已满而覆盖了旧元素则返回 true
    bool push(const T& value) noexcept;

    /// 从队头弹出一个元素。
    ///
    /// @param out 接收弹出值的指针，不可为 null
    /// @return 缓冲区为空时返回 false 且不写 out；成功返回 true
    bool pop(T* out) noexcept;

    /// 返回当前元素个数。
    std::size_t size() const noexcept { return m_size; }

    /// 返回构造时指定的固定容量。
    std::size_t capacity() const noexcept { return m_capacity; }

    /// 判断缓冲区是否为空。
    bool isEmpty() const noexcept { return m_size == 0; }

private:
    T* m_storage;          ///< 连续元素存储（operator new 分配的原始内存）
    std::size_t m_capacity; ///< 总容量
    std::size_t m_head;     ///< 队头下标（下一个弹出位置）
    std::size_t m_size;     ///< 当前元素个数
};

} // namespace freemodel
