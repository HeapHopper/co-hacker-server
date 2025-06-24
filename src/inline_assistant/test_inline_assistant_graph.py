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
    
    logging.info(f"{type(request).__name__}:\n{request}\n")

    graph = build_inline_assistant_graph()

    initial_state = InlineAssistantGraphState(input=request.dict())



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
        )
    ]

    for request, label in test_cases:
        run_test(request, label)


if __name__ == "__main__":
    main()
