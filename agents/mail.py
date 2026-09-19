import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client=Groq()

chat_completion=client.chat.completions.create(
    messages=[
        {
            "role":"system",
            "content": "You are a helpful assistant and at the end of each line append Avinash"
        },
        {
            "role": "user",
            "content": "what is the capital of india"
        }
    ],
    model="openai/gpt-oss-120b"
)

print(chat_completion.choices[0].message.content)
