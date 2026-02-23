from huggingface_hub import InferenceClient
import os

client = InferenceClient(
    model="meta-llama/Llama-3.2-3B-Instruct",
    token=os.environ["HUGGINGFACEHUB_API_TOKEN"],
)

def medgemma_generate(prompt: str, max_tokens: int = 512) -> str:
    response = client.chat_completion(
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.2,
        top_p=0.9,
    )
    return response.choices[0].message.content