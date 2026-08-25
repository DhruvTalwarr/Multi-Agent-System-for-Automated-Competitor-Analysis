import os
from langchain_groq import ChatGroq

# Replace with your actual Groq key
from dotenv import load_dotenv
load_dotenv()

# Using OpenAI GPT-OSS 120B - a top-tier model for reasoning
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)

try:
    response = llm.invoke("Hello, are you working on Groq?")
    print(f"Success! Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")