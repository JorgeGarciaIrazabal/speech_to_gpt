import textwrap

from langchain import GoogleSearchAPIWrapper
from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer

from speech_to_gpt.llms.chat_types import ChatMessage
from speech_to_gpt.llms.open_ai_client import GENERIC_MODEL, get_client


def search_online(question: str, news: bool = False):
    wrapper = GoogleSearchAPIWrapper()

    yield ChatMessage(role="log_message", content="searching online")
    res = wrapper.results(question, 3)
    links = [r["link"] for r in res]
    loader = AsyncHtmlLoader(links, verify_ssl=False)
    docs = loader.load()
    yield ChatMessage(role="log_message", content="analyzing online data")
    html2text_transformer = Html2TextTransformer(ignore_links=False, ignore_images=True)
    docs_transformed = html2text_transformer.transform_documents(docs)
    data_in_web = "\nWeb Page: \n".join(d.page_content for d in docs_transformed)
    result = get_client().chat.completions.create(
        model=GENERIC_MODEL,
        temperature=0.0,
        max_tokens=32_000,
        messages=[
            {
                "role": "system",
                "content": textwrap.dedent("""
                You are an assistant that analyzes the content of multiple webpages given by the user.
                Your goal is to give a clear answer of the question provided.
                Other Instructions: 
                    - Do not use other sources to answer the question other than the provided data
                    - Provide links included in the provided data so users can follow up
                    - Do not mention that the source is HTML or a webpage or an article
                    - The answer should not be more than 200 words
                    - Do not include Footer links, copyright information, or any other irrelevant information
                """),
            },
            {
                "role": "user",
                "content": f"""Based on this data: 

```
{data_in_web}
```
Answer the following: {question}
""",
            },
        ],
        stream=True,
    )
    for m in result:
        if m.choices[0].delta.content:
            message = ChatMessage(role="assistant", content=m.choices[0].delta.content)
            yield message
