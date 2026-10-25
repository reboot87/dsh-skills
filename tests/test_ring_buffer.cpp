#include "freemodel/ring_buffer.h"

#include <cstdio>
#include <type_traits>

namespace {

// ---------------------------------------------------------------------------
// 编译期检查（skill 项目要求第 4 条）：每个对外接口至少一条编译期实例化。
// 这些 static_assert 不生成运行时代码，编译通过即接口契约成立。
// ---------------------------------------------------------------------------

// RingBuffer<int> 必须可显式构造、可移动、不可拷贝。
static_assert(std::is_constructible<freemodel::RingBuffer<int>, std::size_t>::value,
              "RingBuffer<int> must be constructible from a capacity");
static_assert(std::is_nothrow_move_constructible<freemodel::RingBuffer<int>>::value,
              "RingBuffer move construction must be noexcept");
static_assert(!std::is_copy_constructible<freemodel::RingBuffer<int>>::value,
              "RingBuffer must not be copy-constructible");

// 声明的导出实例化类型必须存在且完整（sizeof 对不完整类型无法编译，
// 用指针的完整类型检查替代不存在的 std::is_complete_type —— C++11 标准写法）。
static_assert(sizeof(freemodel::RingBuffer<int>) > 0,
              "RingBuffer<int> must be a complete type");
static_assert(!std::is_same<freemodel::RingBuffer<int>, freemodel::RingBuffer<double>>::value,
              "distinct instantiations must be distinct types");

// ---------------------------------------------------------------------------
// 极简断言框架：不依赖第三方库，不依赖网络（skill 项目要求第 4 条）。
// ---------------------------------------------------------------------------
int g_failures = 0;

#define CHECK(cond)                                                       \
    do {                                                                  \
        if (cond) {                                                        \
            std::printf("PASS %s\n", #cond);                               \
        } else {                                                           \
            std::printf("FAIL %s (line %d)\n", #cond, __LINE__);           \
            ++g_failures;                                                  \
        }                                                                  \
    } while (false)

// LCOV_EXCL_START
void testPushPopBasics() {
    freemodel::RingBuffer<int> buffer(2);
    CHECK(buffer.isEmpty());
    CHECK(buffer.capacity() == 2);

    int value = 0;
    CHECK(!buffer.pop(&value)); // 空缓冲区 pop 必须失败
    CHECK(!buffer.push(10));    // 未满时 push 不覆盖，按文档返回 false
    CHECK(!buffer.push(20));    // 仍未满，返回 false（无覆盖）
    CHECK(buffer.size() == 2);
    CHECK(buffer.pop(&value) && value == 10);
    CHECK(buffer.pop(&value) && value == 20);
    CHECK(buffer.isEmpty());
}
// LCOV_EXCL_STOP

void testOverwriteOldest() {
    freemodel::RingBuffer<int> buffer(3);
    buffer.push(1);
    buffer.push(2);
    buffer.push(3);
    CHECK(buffer.push(4)); // 覆盖 1

    int value = 0;
    CHECK(buffer.pop(&value) && value == 2);
    CHECK(buffer.pop(&value) && value == 3);
    CHECK(buffer.pop(&value) && value == 4);
    CHECK(buffer.isEmpty());
}

void testMoveSemantics() {
    freemodel::RingBuffer<int> buffer(2);
    buffer.push(7);
    buffer.push(8);

    freemodel::RingBuffer<int> moved(static_cast<freemodel::RingBuffer<int>&&>(buffer));
    CHECK(buffer.isEmpty()); // 被移动后的对象处于有效空状态
    CHECK(moved.size() == 2);

    int value = 0;
    CHECK(moved.pop(&value) && value == 7);

    freemodel::RingBuffer<int> target(1);
    target.push(99);
    target = static_cast<freemodel::RingBuffer<int>&&>(moved);
    CHECK(moved.isEmpty());
    CHECK(target.size() == 1);
    CHECK(target.pop(&value) && value == 8); // target 原有的 99 被释放
}

void testWrapAround() {
    // 多轮环绕：容量 3，压入并弹出交错，验证下标取模逻辑。
    freemodel::RingBuffer<int> buffer(3);
    int value = 0;
    for (int round = 0; round < 5; ++round) {
        buffer.push(round * 3 + 1);
        buffer.push(round * 3 + 2);
        buffer.push(round * 3 + 3);
        CHECK(buffer.pop(&value) && value == round * 3 + 1);
        CHECK(buffer.pop(&value) && value == round * 3 + 2);
        CHECK(buffer.pop(&value) && value == round * 3 + 3);
    }
    CHECK(buffer.isEmpty());
}

} // namespace

int main() {
    testPushPopBasics();
    testOverwriteOldest();
    testMoveSemantics();
    testWrapAround();
    if (g_failures == 0) {
        std::printf("ALL TESTS PASSED\n");
        return 0;
    }
    std::printf("%d FAILURE(S)\n", g_failures);
    return 1;
}
