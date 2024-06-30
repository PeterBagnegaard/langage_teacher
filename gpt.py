#import openai
from openai import OpenAI
client = OpenAI()

class ChatBot:
    
    def __init__(self, model="gpt-3.5-turbo", stream=False):
        self.model = model
        self.stream = stream
        self.chatbot = client.chat.completions
        self.system_prompt = [{"role": "system", "content": "You are a language teacher having a conversation with a student."}]
    
    def __call__(self, messages):
        chat_completion = self.chatbot.create(messages=self.system_prompt + messages,
                                              model=self.model,
                                              stream=self.stream)
        
        return chat_completion.choices[0].message.content

if __name__ == '__main__':
    chatbot = ChatBot()
    
    messages=[
        {"role": "user", "content": "Who are you?"}
      ]
    
    res = chatbot(messages)
    print(res)

#%%
"""
Streaming
"""
# https://cookbook.openai.com/examples/how_to_stream_completions
# response = client.chat.completions.create(
#     model='gpt-3.5-turbo',
#     messages=messages,
#     stream=True  # this time, we set stream=True
# )

# for chunk in response:
#     print(chunk.choices[0].delta.content)
