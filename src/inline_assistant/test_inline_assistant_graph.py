import logging
from inline_assistant_models import (
    InlineAssistantRequest,
    InlineAssistantResponse,
    Vulnerability,
)

from inline_assistant.inline_assistant_graph import (
    build_inline_assistant_graph,
    InlineAssistantGraphState,
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')


def run_test(request: InlineAssistantRequest, label: str):
    logging.info(f"\n===== TEST CASE: {label} =====")
    
    graph = build_inline_assistant_graph()

    initial_state = InlineAssistantGraphState(input=request.model_dump())



    # Run the graph
    final_state = graph.invoke(initial_state)

    # Print final output
    response: InlineAssistantResponse = final_state["output"]
    logging.info(f"Output:\n{response}\n")
    logging.info("State Info:")
    logging.info(f"  Confidence Level: {final_state['confidence_level']}")
    logging.info(f"  Unsafe Detected:  {final_state['unsafe_pattern_detected']}")
    logging.info(f"  Suggestion Type:  {final_state['suggestion_type']}")
    logging.info("=" * 40)


def main():
    test_cases = [
        (
            InlineAssistantRequest(
                current_line="strcpy(buffer, user_input);",
                current_scope="""
void process_input(char* user_input) {
    char buffer[100];
    strcpy(buffer, user_input);
}
""".strip(),
                current_file="""
#include <string.h>

void process_input(char* user_input) {
    char buffer[100];
    strcpy(buffer, user_input);
}
""".strip()
            ),
            "Potential buffer overflow"
        ),
        (
            InlineAssistantRequest(
                current_line="std::vector<int> v = {1,2,3};",
                current_scope="""
int main() {
    std::vector<int> v = {1,2,3};
    return 0;
}
""".strip(),
                current_file="""
#include <vector>

int main() {
    std::vector<int> v = {1,2,3};
    return 0;
}
""".strip()
            ),
            "Safe C++ STL usage"
        ),
        (
            InlineAssistantRequest(
                current_line="auto it = m.find(k); if(it != m.end()) { use(it->second); }",
                current_scope="""
void lookup() {
    std::map<int, std::string> m;
    int k = 1;
    auto it = m.find(k);
    if(it != m.end()) {
        use(it->second);
    }
}
""".strip(),
                current_file="""
#include <map>
#include <string>

void use(const std::string& val) {
    // placeholder function
}

void lookup() {
    std::map<int, std::string> m;
    int k = 1;
    auto it = m.find(k);
    if(it != m.end()) {
        use(it->second);
    }
}
""".strip()
            ),
            "Correct map lookup"
        ),
        (
            InlineAssistantRequest(
                current_line="char* p = malloc(100);",
                current_scope="""
void legacy_alloc() {
    char* p = malloc(100);
    // no free
}
""".strip(),
                current_file="""
#include <stdlib.h>

void legacy_alloc() {
    char* p = malloc(100);
    // no free
}
""".strip()
            ),
            "Manual allocation without cleanup"
        ),
        (
            InlineAssistantRequest(
                current_line="memcpy(buffer, data, len);",
                current_scope="""
void copy_data(const char* data, size_t len) {
    char buffer[64];
    if (len < 64) {
        memcpy(buffer, data, len);
    }
}
""".strip(),
                current_file="""
#include <string.h>
#include <stddef.h>

void copy_data(const char* data, size_t len) {
    char buffer[64];
    if (len < 64) {
        memcpy(buffer, data, len);
    }
}
""".strip()
            ),
            "Bounds-checked memcpy (edge case for static analyzers)"
        ),
        (
            InlineAssistantRequest(
                current_line="strcat(buffer, input);",
                current_scope="""
void append_user_input(char* buffer, const char* input) {
    if (strlen(input) < 32) {
        strcat(buffer, input);
    }
}
""".strip(),
                current_file="""
#include <string.h>

void append_user_input(char* buffer, const char* input) {
    if (strlen(input) < 32) {
        strcat(buffer, input);
    }
}
""".strip()
            ),
            "Potential unsafe strcat with length check"
        ),
        (
            InlineAssistantRequest(
                current_line="delete obj;",
                current_scope="""
void cleanup() {
    MyClass* obj = new MyClass();
    // use obj
    delete obj;
}
""".strip(),
                current_file="""
class MyClass {
public:
    MyClass() {}
    ~MyClass() {}
};

void cleanup() {
    MyClass* obj = new MyClass();
    // use obj
    delete obj;
}
""".strip()
            ),
            "Manual delete - potential for RAII upgrade suggestion"
        ),
        (
            InlineAssistantRequest(
                current_line="FILE* f = fopen(filename, \"r\");",
                current_scope="""
void read_file(const char* filename) {
    FILE* f = fopen(filename, "r");
    if (f) {
        char buf[128];
        fread(buf, 1, sizeof(buf), f);
        fclose(f);
    }
}
""".strip(),
                current_file="""
#include <stdio.h>

void read_file(const char* filename) {
    FILE* f = fopen(filename, "r");
    if (f) {
        char buf[128];
        fread(buf, 1, sizeof(buf), f);
        fclose(f);
    }
}
""".strip()
            ),
            "Legacy C file I/O - might suggest upgrade to modern std::ifstream"
        ),
        (
            InlineAssistantRequest(
                current_line="char c = *(p + 5);",
                current_scope="""
void parse(char* p) {
    if (p != nullptr) {
        char c = *(p + 5);
        process(c);
    }
}
""".strip(),
                current_file="""
void process(char c) {
    // do something
}

void parse(char* p) {
    if (p != nullptr) {
        char c = *(p + 5);
        process(c);
    }
}
""".strip()
            ),
            "Pointer arithmetic with weak bounds checking"
        ),
        (
            InlineAssistantRequest(
                current_line="std::unique_ptr<MyClass> obj(new MyClass());",
                current_scope="""
void init() {
    std::unique_ptr<MyClass> obj(new MyClass());
    obj->run();
}
""".strip(),
                current_file="""
#include <memory>

class MyClass {
public:
    void run() {}
};

void init() {
    std::unique_ptr<MyClass> obj(new MyClass());
    obj->run();
}
""".strip()
            ),
            "Modern smart pointer usage (safe)"
        ),
        (
            InlineAssistantRequest(
                current_line="return str[0] == '\\0';",
                current_scope="""
bool is_empty(const char* str) {
    if (str == nullptr) return true;
    return str[0] == '\\0';
}
""".strip(),
                current_file="""
bool is_empty(const char* str) {
    if (str == nullptr) return true;
    return str[0] == '\\0';
}
""".strip()
            ),
            "Null-pointer check pattern"
        ),
                (
            InlineAssistantRequest(
                current_line="if (strlen(input) > sizeof(buffer)) strcpy(buffer, input);",
                current_scope="""
void insecure_copy(const char* input) {
    char buffer[64];
    if (strlen(input) > sizeof(buffer)) strcpy(buffer, input);
}
""".strip(),
                current_file="""
#include <string.h>

void insecure_copy(const char* input) {
    char buffer[64];
    if (strlen(input) > sizeof(buffer)) strcpy(buffer, input);
}
""".strip()
            ),
            "Conditional buffer overflow (logic flaw)"
        ),
        (
            InlineAssistantRequest(
                current_line="delete ptr;",
                current_scope="""
void unsafe_delete() {
    int* ptr = new int(5);
    delete ptr;
    delete ptr; // double free
}
""".strip(),
                current_file="""
#include <iostream>

void unsafe_delete() {
    int* ptr = new int(5);
    delete ptr;
    delete ptr; // double free
}
""".strip()
            ),
            "Double delete (memory corruption)"
        ),
        (
            InlineAssistantRequest(
                current_line="char* tmp = getenv(\"PATH\");",
                current_scope="""
void read_env() {
    char* tmp = getenv("PATH");
    printf("PATH=%s\\n", tmp);
}
""".strip(),
                current_file="""
#include <stdlib.h>
#include <stdio.h>

void read_env() {
    char* tmp = getenv("PATH");
    printf("PATH=%s\\n", tmp);
}
""".strip()
            ),
            "Safe but old-school getenv usage"
        ),
        (
            InlineAssistantRequest(
                current_line="std::auto_ptr<int> p(new int(10));",
                current_scope="""
void deprecated_ptr() {
    std::auto_ptr<int> p(new int(10));
    std::cout << *p << std::endl;
}
""".strip(),
                current_file="""
#include <memory>
#include <iostream>

void deprecated_ptr() {
    std::auto_ptr<int> p(new int(10));
    std::cout << *p << std::endl;
}
""".strip()
            ),
            "Use of deprecated std::auto_ptr"
        ),
        (
            InlineAssistantRequest(
                current_line="strncpy(dst, src, strlen(src));",
                current_scope="""
void misuse_strncpy(const char* src) {
    char dst[64];
    strncpy(dst, src, strlen(src));
}
""".strip(),
                current_file="""
#include <string.h>

void misuse_strncpy(const char* src) {
    char dst[64];
    strncpy(dst, src, strlen(src));
}
""".strip()
            ),
            "Misuse of strncpy (wrong size argument)"
        )

    ]

    for request, label in test_cases:
        run_test(request, label)

if __name__ == "__main__":
    main()
