import json
import logging
import textwrap

import tenacity
from tenacity import after_log

from speech_to_gpt.llms.actions.search_online import search_online
from speech_to_gpt.llms.chat_types import ChatMessage
from speech_to_gpt.llms.open_ai_client import (
    lm_studio_client,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

functions = [
    {
        "name": "search_online",
        "description": "Search online for specific topic or question",
        "parameters": {
            "question": {
                "type": "string",
                "description": "Question to search for. The question should be in a way that DuckDuckGo can easily find the answer. The question sent to the function should be aligned in meaning with the user's question.",
            }
        },
    },
    {
        "name": "no_action",
        "description": "Action representing that no action is required.",
        "parameters": {},
    },
]


system_message = {
    "role": "system",
    "content": textwrap.dedent(f"""
        You are a LLM agent that decides if it is worth it to run  one of the following actions or not.
        If the question does not require any of the following actions just response an empty json.
        
        Actions:
        ```json
        {json.dumps(functions[0], indent=4)}
        ```
                
        Response with the action to take and its parameters if a format like in this example (but only if the action is required):
        ```json
        {{
            "action": "the name of the function to execute",
            "parameters": {{
                "question": "what is the current stock price of AAPL?"
            }}
        }}
        ```
        
        If no action is required like "tell me a joke", "tell me a story", etc. return an empty json like:
        ```
        {{}}
        ```
        
        IMPORTANT: 
        - Response with the json only. DO NOT explain how to use the the function. 
        - The output will be used by a computer
        """),
}


string_to_function_map = {
    "search_online": search_online,
}


@tenacity.retry(
    wait=tenacity.wait_fixed(0),
    stop=tenacity.stop_after_attempt(2),
    after=after_log(logger, logging.INFO),
)
def get_required_actions(message: ChatMessage):
    print("staring_get_required_actions")
    result = lm_studio_client.chat.completions.create(
        model="bubu",
        functions=functions,
        messages=[system_message, message.model_dump()],
    )
    content = result.choices[0].message.content
    # extract json from content
    print(content)
    content = "{" + content.split("{", 1)[-1].rsplit("}", 1)[0] + "}"
    content = json.loads(content)
    if (
        content.get("action") == "no_action"
        or content.get("action") not in string_to_function_map
    ):
        return {}
    return content


if __name__ == "__main__":
    message = ChatMessage(
        role="user",
        content="how to make my daughter happy?",
    )
    result = get_required_actions(message)
