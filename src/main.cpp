#include "freemodel/ring_buffer.h"

#include <cstdio>

int main() {
    freemodel::RingBuffer<int> buffer(3);

    // 压入 3 个元素：1 2 3
    buffer.push(1);
    buffer.push(2);
    buffer.push(3);

    // 缓冲区已满，再压入 4 会覆盖最旧的 1，缓冲区变为 2 3 4
    const bool overwritten = buffer.push(4);
    std::printf("push(4) overwrote oldest: %s\n", overwritten ? "true" : "false");

    // 依次弹出：2 3 4，然后缓冲区变空
    int value = 0;
    while (buffer.pop(&value)) {
        std::printf("popped: %d (size=%zu)\n", value, buffer.size());
    }

    // 空缓冲区 pop 返回 false
    const bool emptyPop = buffer.pop(&value);
    std::printf("pop on empty: %s\n", emptyPop ? "true" : "false");
    return 0;
}
