from openai import OpenAI

class OpenAIProvider:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def generate_response(self, prompt, model="gpt-3.5-turbo", max_tokens=150):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return response['choices'][0]['message']['content']

    def set_api_key(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)