from langchain.document_loaders import AsyncHtmlLoader
from langchain.document_transformers import Html2TextTransformer
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from openai import OpenAI

GENERIC_MODEL = "llama3:latest"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)


def search_online(topic: str, news: bool = False):
    wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
    res = wrapper.results(topic, 5, backend="api")
    loader = AsyncHtmlLoader([r["link"] for r in res], verify_ssl=False)
    html2text = Html2TextTransformer()
    docs = loader.load()
    docs_transformed = html2text.transform_documents(docs)
    docs_transformed[0].page_content[0:500]
    return client.chat.completions.create(
        model=GENERIC_MODEL,
        messages=[{"role": "user", "content": f"search_online {search}"}],
        stream=True,
    )
