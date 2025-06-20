#!/usr/bin/env python3

"""
- have initial prompt
- then formulate python script
- execute python script
- check if result is pandas dataframe
- if so, convert to markdown
- formulate reply
- create python code that can plot a chart
- plot it
- create html page with full result
"""

import markdown
import webbrowser
import os
from chat import chat_response, add_to_history


message = """
You are a financial software engineer.
Assumptions:

- Coupon: 5%
- Duration: 1 year
- Initial investment: 100

Scenarios:

- Sale at 98
- Sale at 100
- Sale at 102

"""

message_rules = """
"""

message_instruction = """
Create python that calculates it.

GUIDELINE:

- Return pure Python code without explanation
- Create a function that returns a pandas dataframe
- The last line of the script calls the function and saves result to variable `result`
- Don't write if `__name__ == "__main__"` construct
- Don't print result
"""

message1 = message + message_rules + message_instruction


def code_message_cleaner(code: str):
    """Various heuristics to clean LLM code response."""
    return code.replace("```python", "").replace("```", "")


result1 = chat_response(message1)


def exec_wrapper(code: str):
    namespace = {}
    exec(code, namespace)
    return namespace["result"]


result2 = exec_wrapper(code_message_cleaner(result1.content))


message2 = f"""
Result of calculation is:

{result2.to_markdown()}

Formulate an answer. Explain briefly how calculation was made."""

result3 = chat_response(message2, history=add_to_history(message, history=[]))


message3 = """
Compare the scenarios by plotting a chart.

RULES:

- create bar chart
- sales price is categorical

GUIDELINE:

- use matplotlib package to draw chart
- Return pure Python code without explanation or markdown delimiters for code.
- Return code WITHOUT backticks
- Don't write if `__name__ == "__main__"` construct
- Don't print result
- Don't save plot
- The last line of the script calls the function and set plot to variable `result`
"""


result4 = chat_response(
    message3,
    history=[{"role": "user", "content": m} for m in [message, message2]],
)

plot = exec_wrapper(code_message_cleaner(result4.content))
plot.savefig("plot.png")


colors = ["rgba(255, 0, 0, 0.1)", "rgba(0, 0, 255, 0.1)"]


html = markdown.markdown(
    "\n\n----\n\n".join(
        [
            message + message_instruction,
            result1.content,
            message2,
            result3.content,
            message3,
            result4.content,
            "![plot](/Users/phi/Documents/Coding/chat_client_pdf/plot.png)",
        ]
    ),
    extensions=["tables", "fenced_code", "codehilite"],
)

sections = [
    message + message_instruction,
    result1.content + "\n\n" + result2.to_markdown(),
    message2,
    result3.content,
    message3,
    result4.content
    + "\n\n![plot](/Users/phi/Documents/Coding/chat_client_pdf/plot.png)",
]


def print_last_conv(message: str, result: str):

    colored_html_sections = [
        f'<div style="background-color: {colors[0]}; padding: 10px; margin-bottom: 10px;">{markdown.markdown(message, extensions=['tables', 'fenced_code', 'codehilite'])}</div>',
        f'<div style="background-color: {colors[1]}; padding: 10px; margin-bottom: 10px;">{markdown.markdown(result, extensions=['tables', 'fenced_code', 'codehilite'])}</div>',
    ]
    html = "\n".join(colored_html_sections)
    with open("./temp_conv.html", "w") as f:
        f.write(html)

    # Open in browser
    webbrowser.open("file:///Users/phi/Documents/Coding/chat_client_pdf/temp_conv.html")

    return None


print_last_conv("test", "answer")


colored_html_sections = [
    f'<div style="background-color: {colors[i % 2]}; padding: 10px; margin-bottom: 10px;">{markdown.markdown(section, extensions=['tables', 'fenced_code', 'codehilite'])}</div>'
    for i, section in enumerate(sections)
]
html = "\n".join(colored_html_sections)


with open("./conversation.html", "w") as f:
    f.write(html)

# Open in browser
# webbrowser.open("file:///Users/phi/Documents/Coding/chat_client_pdf/conversation.html")
