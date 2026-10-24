#include "freemodel/ring_buffer.h"

#include <new>

namespace freemodel {

template <typename T>
RingBuffer<T>::RingBuffer(std::size_t capacity)
    : m_storage(nullptr),
      m_capacity(capacity),
      m_head(0),
      m_size(0) {
    // operator new 只分配原始内存，不构造任何 T 对象（配合 placement new 使用）。
    // 元素在 push 时用 placement new 构造，在 pop 时显式调用析构，避免 T 的
    // 默认构造要求，也让未使用的槽位不持有任何活跃对象。
    m_storage = static_cast<T*>(::operator new(capacity * sizeof(T)));
}

template <typename T>
RingBuffer<T>::~RingBuffer() noexcept {
    if (m_storage == nullptr) {
        return;
    }
    while (m_size > 0) {
        m_storage[m_head].~T();
        m_head = (m_head + 1) % m_capacity;
        --m_size;
    }
    ::operator delete(m_storage);
}

template <typename T>
RingBuffer<T>::RingBuffer(RingBuffer&& other) noexcept
    : m_storage(other.m_storage),
      m_capacity(other.m_capacity),
      m_head(other.m_head),
      m_size(other.m_size) {
    other.m_storage = nullptr;
    other.m_capacity = 0;
    other.m_head = 0;
    other.m_size = 0;
}

template <typename T>
RingBuffer<T>& RingBuffer<T>::operator=(RingBuffer&& other) noexcept {
    if (this == &other) {
        return *this;
    }
    // 先释放自身资源，再接管 other 的。
    while (m_size > 0) {
        m_storage[m_head].~T();
        m_head = (m_head + 1) % m_capacity;
        --m_size;
    }
    ::operator delete(m_storage);
    m_storage = other.m_storage;
    m_capacity = other.m_capacity;
    m_head = other.m_head;
    m_size = other.m_size;
    other.m_storage = nullptr;
    other.m_capacity = 0;
    other.m_head = 0;
    other.m_size = 0;
    return *this;
}

template <typename T>
bool RingBuffer<T>::push(const T& value) noexcept {
    // 若槽位上已有活跃对象（覆盖写），必须先析构再 placement new，
    // 保证同一个位置任意时刻最多只有一个活跃 T 对象。
    const bool overwritten = m_size == m_capacity;
    const std::size_t writePos = (m_head + m_size) % m_capacity;
    if (overwritten) {
        m_storage[m_head].~T();
        m_head = (m_head + 1) % m_capacity;
        --m_size;
    }
    new (&m_storage[writePos]) T(value);
    ++m_size;
    return overwritten;
}

template <typename T>
bool RingBuffer<T>::pop(T* out) noexcept {
    if (m_size == 0) {
        return false;
    }
    *out = m_storage[m_head];
    m_storage[m_head].~T();
    m_head = (m_head + 1) % m_capacity;
    --m_size;
    return true;
}

// 显式实例化：本库对外承诺支持的元素类型。新增类型需在此追加，
// 并同步更新 docs/ring-buffer.md。
template class RingBuffer<int>;
template class RingBuffer<double>;

} // namespace freemodel
