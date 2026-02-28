from openai import OpenAI
import asyncio

class OpenAi:
    def __init__(self,api_key:str,base_url:str="https://integrate.api.nvidia.com/v1",model:str="openai/gpt-oss-20b"):
        '''Initializes the OpenAI client with the provided API key.'''
        client=OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.client=client
        self.model=model
    
    async def invoke_model(self,messages:list=[{"role":"user","content":""}])->str:
        '''Invokes the OpenAI model with the given prompt and returns the response.'''
        if not self.client:
            raise Exception("Client not initialized")
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=1,
        top_p=1,
        max_tokens=4096,
        stream=True
        )
        full_response = ""
        for chunk in completion:
            if not getattr(chunk, "choices", None):
                continue
            reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
            if reasoning:pass
                # print(reasoning, end="")
            if chunk.choices and chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                # print(content, end="")
                full_response += content
        return full_response
                
        
                
                
            
