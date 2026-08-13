from groq import Groq

from config.settings import settings


client = Groq(
    api_key=settings.GROQ_API_KEY
)


def ask_llm(prompt: str):

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content