from dotenv import load_dotenv
import os
import pyttsx3
from pydantic import BaseModel
import json
from llm_model.open_ai import OpenAi
from agent_tools import Tools
from agent_tools.mcp_method import MCPClient,MCPTool
from agent_core import BuildAgent
import webbrowser
import urllib.parse
load_dotenv()
import asyncio

API_KEY = os.getenv("API_KEY")
client = OpenAi(api_key=API_KEY)


#tool to open search query in web browser
model1_tools = Tools()
@model1_tools.add_tool
def web_search(url: str) -> str:
    """
    Open a web search/website for the given url using the default web browser.

    :param url: The search url to be opened.  
                  - If it starts with http:// or https://, open it directly.  
                  - Otherwise, treat it as a Google search term.
    :return: A short status message.
    """
    try:
        url = url.strip()
        if url.startswith("http://") or url.startswith("https://"):
            url = url
        else:
            encoded = urllib.parse.quote_plus(url)
            url = f"https://www.google.com/search?q={encoded}"

        webbrowser.open(url)
        return f"Opened: {url}"
    except Exception as e:
        return f"Error: {e}"
@model1_tools.add_tool
def text_to_speech(text:str, rate:int=150, volume:float=1.0, voice_index:int=0):
    """
    Convert text to speech using pyttsx3.
    
    :param text: The text to be spoken.
    :param rate: Speech rate (default 150 words per minute).
    :param volume: Volume level (0.0 to 1.0).
    :param voice_index: Index of the voice to use (0 for male, 1 for female in most systems).
    """
    try:
        # Initialize the TTS engine
        engine = pyttsx3.init()

        # Set speaking rate
        engine.setProperty('rate', rate)

        # Set volume
        engine.setProperty('volume', volume)

        # Get available voices and set one
        voices = engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
        else:
            print(f"Invalid voice index. Using default voice.")

        # Speak the text
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"Error: {e}")


    

def main():
    agent = BuildAgent(name="Model1", description="This is a test agent",
                       llm_client=client, tools=model1_tools, memory_collection_name="rawagent_memory",
                       system_prompt='You are a helpful ai agent which can use tools, help me with the tasks')

    while True:
        query = input('\nenter question: ')
        if query.lower() in ['exit', 'quit']:
            break
        response = agent.run_agent_sync(query)
        
if __name__ == "__main__":
    main()
