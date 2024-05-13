from openai import OpenAI

GENERIC_MODEL = "llama3:8b-instruct-q8_0"
# GENERIC_MODEL = "mixtral:latest"
# GENERIC_MODEL = "llama3:latest"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)
lm_studio_client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lmstudio",  # required, but unused
)


def get_client():
    return client
    # return lm_studio_client
