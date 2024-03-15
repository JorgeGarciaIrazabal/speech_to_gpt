import json

import tenacity
from speech_to_gpt.llms.chat_types import QuestionMessage
from ollama import Client


MODEL = "mistral:latest"

promt = """from the following question.
Question: 
```
{question}
```

what are the aditional questions to ask the user to clarify the context? Ask as many question as you consider necessary.

Answer only in JSON format like the following example:
```json
[
    {{
        "question": "what kind of story do you want to hear?",
        "type": "choice",
        "choices": ["adventure", "romance", "mystery"]
    }},
    {{
        "question": "what is the name of the main character?",
        "type": "text",
        "choices": []
    }},
    {{
        "question": "how old if the main character?",
        "type": "numeric",
        "choices": []
    }}
]
```
"type" can be numeric, text, date, or choice. If the type is choice, the choices field must be filled.


```
"""

def get_questions_to_expand_context(user_question: str) -> list[QuestionMessage]:
    exception = None
    for i in range(3):
        formated_promt = promt.format(question=user_question)
        if exception:
            formated_promt = f"""
{formated_promt}
Previously, you gut the following exception:
```
{exception}
```
try to fix the json.
"""
        try:
            aditional_questions = Client().generate(
                model=MODEL,
                system="You are a promt engineer with experience getting the most out of llms",
                prompt=formated_promt,
            )["response"]
            #extract json from additonal questions
            try:
                aditional_question_dict = json.loads(aditional_questions.split("```json")[1].split("```")[0].strip())
            except (IndexError, json.JSONDecodeError):
                aditional_question_dict = json.loads(aditional_questions.strip())

            return [QuestionMessage(**question) for question in aditional_question_dict]
        except Exception as e:
            print(e)
            exception = e
    if exception:
        raise exception