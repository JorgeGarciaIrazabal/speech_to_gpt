import json
import textwrap

import tenacity
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.embeddings import OllamaEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.vectorstores import Chroma

from speech_to_gpt import ChatMessage
from speech_to_gpt.llms.open_ai_client import (
    client,
    GENERIC_MODEL,
)

from langchain.agents import Tool

ddg_search = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="DuckDuckGo Search",
        func=ddg_search.run,
        description="Useful to browse information from the Internet.",
    )
]

functions = [
    {
        "name": "search_online",
        "description": "Search online for specific topic or question",
        "parameters": {
            "topic": {
                "type": "string",
                "description": "Topic to search for in a way that the search engine DuckDuckGo can understand",
            },
            "news": {"type": "boolean", "description": "Search only for news"},
        },
    }
]


system_message = {
    "role": "system",
    "content": textwrap.dedent(f"""
        You are a LLM agent in charge of choosing zero or one action to take based on the user's message.
        The allow functions have the follow format:
        ```json
        {json.dumps(functions[0], indent=4)}
        ```

        Return with the action to take and its parameters like in this example:
        ```json
        {{
            "action": "the name of the function to execute",
            "parameters": {{
                "topic": "what is the current stock price of AAPL?",
                "news": true
            }}
        }}
        ```
        Response only in JSON format.
        """),
}


def search_online(topic: str, news: bool = False):
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
    res = wrapper.results(topic, 3, backend="api")
    links = [r["link"] for r in res]
    loader = AsyncHtmlLoader(links, verify_ssl=False)
    docs = loader.load()
    html2text_transformer = Html2TextTransformer()
    docs_transformed = html2text_transformer.transform_documents(docs)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.create_documents([d.page_content for d in docs_transformed])
    ollama_emb = OllamaEmbeddings(
        model="nomic-embed-text",
    )
    # embed_texts = ollama_emb.embed_documents(texts)
    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=ollama_emb,
    )
    docs = vectordb.similarity_search(topic, k=3)
    print("docs embeded")
    content_data = {"\n".join(d.page_content for d in docs)}
    result = client.chat.completions.create(
        model=GENERIC_MODEL,
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that analyzes the content of multiple webpages."
                " to give a clear and concise answer of the question provided."
                " Do not provide information of where did you find the information, just answer the question",
            },
            {
                "role": "user",
                "content": f"""Based on this data: 

```
Web Page 1:
{content_data}
```
answer the following question: {topic}
""",
            },
        ],
        stream=False,
    )
    print(result.choices[0].message.content)


string_to_function_map = {
    "search_online": search_online,
}


@tenacity.retry(wait=tenacity.wait_fixed(0), stop=tenacity.stop_after_attempt(3))
def get_required_actions(message: ChatMessage):
    print("staring_get_required_actions")
    result = client.chat.completions.create(
        model="phi3:instruct",
        functions=functions,
        messages=[system_message, message.model_dump()],
    )
    content = result.choices[0].message.content
    # extract json from content
    content = "{" + content.split("{", 1)[-1].rsplit("}", 1)[0] + "}"
    print(content)
    content = json.loads(content)
    print("content", content)
    string_to_function_map[content["action"]](**content["parameters"])


if __name__ == "__main__":
    message = ChatMessage(
        role="user",
        content="latest news about covid?",
    )
    result = get_required_actions(message)
