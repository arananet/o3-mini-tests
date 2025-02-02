"""
This example shows how to create two LangChain agents:
  1. A retrieval agent that uses DeepSeek R1 llm via Ollama (running locally).
  2. A reasoning agent based on OpenAI’s o3-mini llm.
They interact in a loop, each contributing to the final collaborative solution.

Developer Eduardo Arana - info@arananet.net
"""

import os
import time
import requests  # To call the local Ollama endpoint
from langchain_community.llms import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

load_dotenv()


# -------------------------------------
# Step 1: Define DeepSeek R1 access via Ollama locally.
#
# This function calls the local Ollama endpoint that wraps DeepSeek R1.
# Modify the endpoint URL, headers, and payload as necessary.
# -------------------------------------
def deepseek_r1_search(query: str) -> str:
    # URL for your local Ollama instance that runs the DeepSeek R1 model
    ollama_url = "http://localhost:11434/api/generate"  # update to your configuration

    # Payload for your API call; adjust keys as required by Ollama’s API
    payload = {
        "model": "deepseek-r1:1.5b",
        "prompt": query,
        "stream": False
    }
    try:
        print(f"{Fore.CYAN}[DeepSeek R1 via Ollama]{Style.RESET_ALL} Sending query: {query}")
        with tqdm(total=100, desc="Waiting for DeepSeek R1 response", ncols=75) as pbar:
            response = requests.post(ollama_url, json=payload)
            for _ in range(100):
                time.sleep(0.1)  # Simulate waiting time
                pbar.update(1)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()
            # Depending on the API, adjust the way you get the result.
            result = data.get("response", f"Default response for query '{query}'")
    except Exception as e:
        result = f"Error in DeepSeek R1 call: {e}"
    return result

# Wrap the above function as a LangChain Tool
deepseek_tool = Tool(
    name="DeepSeek_Search",
    func=deepseek_r1_search,
    description="Query DeepSeek R1 (via a local Ollama instance) to retrieve relevant documents or information based on a search query."
)


# -------------------------------------
# Step 2: Set up the OpenAI-based reasoning agent.
#
# Use a chat-oriented OpenAI model. (Make sure OPENAI_API_KEY is set in your environment.)
# -------------------------------------
openai_llm = ChatOpenAI(model_name="o3-mini")  # note: o3-mini does not support temperature parameter

# Define a prompt template for the reasoning agent.
reasoning_template = """
You are a collaborative reasoning agent. You will receive search results from DeepSeek R1 and the current state of the conversation.
Your task is to analyze the provided information and suggest the next steps towards solving the problem.

Current conversation/context:
{conversation_history}

DeepSeek result:
{search_result}

Based on the above, provide a next step, a plan, or a summative insight.
Response:
"""

reasoning_prompt = PromptTemplate(
    input_variables=["conversation_history", "search_result"],
    template=reasoning_template
)

# Instead of using LLMChain and its .run() method (which are deprecated),
# chain the prompt and LLM into a RunnableSequence.
reasoning_chain = reasoning_prompt | openai_llm


# -------------------------------------
# Step 3: Create the collaborative multi-agent interaction loop.
#
# Here, the session loop simulates a collaborative exchange:
# – The retrieval agent (DeepSeek R1 via Ollama) returns search results.
# – The reasoning agent (OpenAI) uses this information alongside the conversation history to suggest the next step.
# The interaction continues for a defined number of rounds.
# -------------------------------------
def collaborative_session(initial_query: str, rounds: int = 2):
    conversation_history = f"Initial query: {initial_query}"
    current_query = initial_query

    for i in range(rounds):
        print(f"\n{Fore.YELLOW}=== Round {i+1} ==={Style.RESET_ALL}")

        # 1. Retrieval stage: query DeepSeek R1 through Ollama.
        retrieval_result = deepseek_r1_search(current_query)
        print(f"{Fore.CYAN}DeepSeek R1 response:{Style.RESET_ALL} {retrieval_result}")

        # 2. Reasoning stage: use OpenAI agent to process information.
        reasoning_input = {
            "conversation_history": conversation_history,
            "search_result": retrieval_result
        }
        with tqdm(total=100, desc="Waiting for Reasoning Agent response", ncols=75) as pbar:
            # Use .invoke() instead of .run()
            reasoning_output = reasoning_chain.invoke(input=reasoning_input)
            for _ in range(100):
                time.sleep(0.1)  # Simulate waiting time
                pbar.update(1)
        print(f"{Fore.MAGENTA}O3-Mini agent output:{Style.RESET_ALL} {reasoning_output}")

        # 3. Update conversation history.
        conversation_history += f"\nRound {i+1}:\nSearch query: {current_query}\nDeepSeek result: {retrieval_result}\nReasoning: {reasoning_output}\n"

        # 4. Optionally, use the reasoning output as a basis for the next search query.
        current_query = reasoning_output.content.strip()

        time.sleep(1)  # Optionally pause between rounds.

    print(f"\n{Fore.GREEN}--- Final conversation history ---{Style.RESET_ALL}")
    print(conversation_history)
    return conversation_history


# -------------------------------------
# Main entry point for testing.
# -------------------------------------
if __name__ == "__main__":
    # Ensure that your OpenAI API key is set in your .env file:
    # OPENAI_API_KEY=
    test_query = "What are the latest advancements in natural language processing?"
    collaborative_session(initial_query=test_query, rounds=3)
