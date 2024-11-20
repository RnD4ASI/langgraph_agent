"""
Research Assistant Example

This script demonstrates a single-agent research workflow using the LangGraph framework.
It creates a research assistant that can:
1. Search the web using DuckDuckGo
2. Extract content from webpages
3. Analyze and synthesize information
4. Provide sourced summaries

Key Components:
- Web search tool using DuckDuckGo
- Content scraping tool with BeautifulSoup
- Research agent with comprehensive system message
"""

from typing import List
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage

import sys
import os
# Add parent directory to path to import agent_framework
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_framework import create_single_agent

# Step 1: Define the web search tool
def web_search(query: str, max_results: int = 3) -> List[str]:
    """
    Search the web using DuckDuckGo and return formatted results.
    
    Process:
    1. Initialize DuckDuckGo search session
    2. Execute search with query
    3. Format results with title, snippet, and URL
    4. Handle potential API errors
    
    Args:
        query: Search terms to look up
        max_results: Maximum number of results to return (default: 3)
    
    Returns:
        List of formatted search results with title, description, and URL
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return [f"{r['title']}: {r['body']}\nURL: {r['link']}" for r in results]
    except Exception as e:
        return [f"Error performing search: {str(e)}"]

# Step 2: Define the webpage scraping tool
def scrape_webpage(url: str) -> str:
    """
    Extract and clean content from a webpage.
    
    Process:
    1. Send HTTP request with user agent
    2. Parse HTML with BeautifulSoup
    3. Extract text from paragraphs
    4. Truncate if too long
    5. Handle connection errors
    
    Args:
        url: Web page URL to scrape
    
    Returns:
        Extracted and cleaned text content
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text from paragraphs
            text = ' '.join([p.get_text() for p in soup.find_all('p')])
            return text[:1000] + "..." if len(text) > 1000 else text
        return f"Failed to retrieve webpage: Status code {response.status_code}"
    except Exception as e:
        return f"Error scraping webpage: {str(e)}"

# Step 3: Create LangChain tools
search_tool = Tool(
    name="web_search",
    description="Search the web for information using DuckDuckGo",
    func=web_search
)

scrape_tool = Tool(
    name="scrape_webpage",
    description="Scrape and extract text content from a webpage",
    func=scrape_webpage
)

# Step 4: Define the research assistant's system message
system_message = """You are a research assistant that helps users find and analyze information from the web.
Follow these steps:
1. When given a research question, use the web_search tool to find relevant information
2. If you find interesting URLs, use the scrape_webpage tool to get more detailed content
3. Analyze all the information and provide a comprehensive but concise summary
4. Always cite your sources using the URLs provided

Remember to:
- Focus on credible sources
- Cross-reference information when possible
- Provide balanced viewpoints
- Highlight any uncertainties or conflicting information
"""

def main():
    """
    Main function that runs the research assistant workflow.
    
    Process:
    1. Initialize the research agent
    2. Present example questions
    3. Get user input
    4. Execute research workflow
    5. Display results
    """
    # Step 5: Create the research agent
    agent = create_single_agent(
        system_message=system_message,
        tools=[search_tool, scrape_tool],
        model="gpt-3.5-turbo"
    )
    
    # Step 6: Define example research questions
    questions = [
        "What are the latest developments in quantum computing?",
        "What are the environmental impacts of electric vehicles?",
        "What are the health benefits and risks of intermittent fasting?",
    ]
    
    # Step 7: Set up the interactive interface
    print("Research Assistant Demo")
    print("Available questions:")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
    
    # Step 8: Get user input
    choice = input("\nSelect a question number or type your own question: ")
    try:
        question = questions[int(choice) - 1] if choice.isdigit() and 1 <= int(choice) <= len(questions) else choice
    except (ValueError, IndexError):
        question = choice
    
    print(f"\nResearching: {question}\n")
    
    # Step 9: Execute the research workflow
    result = agent.graph.invoke({
        "messages": [HumanMessage(content=question)],
        "metadata": {"max_turns": 5}  # Limit iterations to prevent infinite loops
    })
    
    # Step 10: Display the research results
    final_message = result["messages"][-1]
    print("\nResearch Summary:")
    print("-" * 80)
    print(final_message.content)
    print("-" * 80)

if __name__ == "__main__":
    main()
