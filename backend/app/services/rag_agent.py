import structlog
from typing import TypedDict, Annotated, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent
from app.config import settings
from langchain_core.tools import tool
from pydantic import BaseModel, Field

logger = structlog.get_logger()

# We need a reference to the RAGService to perform searches
# However, RAGService depends on DB session which is request-scoped.
# To handle this cleanly with LangGraph tools, we can pass the search function
# or inject the context dynamically. 
# A cleaner way is to create the agent dynamically per request or use a wrapper class.

class RAGAgent:
    def __init__(self, rag_service_search_func, user_id: int):
        self.rag_service_search_func = rag_service_search_func
        self.user_id = user_id
        self.api_key = settings.openai_api_key
        self.model_name = settings.llm_model
        self.used_posts = []
        
        # Tools need to be defined here to capture the search_func and user_id via closure
        @tool
        def search_user_posts(query: str) -> str:
            """
            Search the user's monitored social media posts for relevant information.
            Useful for queries asking about news, strategies, or specific crypto/stock tickers.
            Returns formatted text containing relevant posts.
            """
            try:
                posts = self.rag_service_search_func(query, self.user_id, limit=10)
                # Filter posts by relevance
                RELEVANCE_THRESHOLD = 0.35
                relevant_posts = [p for p in posts if p.get('similarity', 0) > RELEVANCE_THRESHOLD]
                
                if not relevant_posts:
                    return "No relevant posts found for this query."
                
                self.used_posts.extend(relevant_posts)
                
                context_parts = []
                for i, post in enumerate(relevant_posts, 1):
                    # Including URL for citation tracking later if needed
                    context_parts.append(f"Post [{i}]: {post['text']}")
                
                return "\n\n".join(context_parts)
            except Exception as e:
                logger.error("Error in search_user_posts tool", error=str(e))
                return f"Error executing search: {str(e)}"
        
        self.tools = [search_user_posts]
        
        self.system_prompt = """You are an Expert Crypto/Stock Trading Analyst who is also a helpful assistant.
        
Your goal is to answer the user's question. If the question requires knowledge from the user's monitored feeds, you MUST use the `search_user_posts` tool to retrieve relevant posts.

**MODE 1: TRADE STRATEGY**
If the user explicitly asks for a "strategy", "signal", "trade idea", or specific financial advice about a ticker (e.g., "Trade strategy for BTC", "Should I buy SOL?"), you MUST output a structured analysis in this format:

## Trade Strategy: [TICKER]
**Signal:** [LONG/SHORT/NEUTRAL]
**Confidence:** [High/Medium/Low]

*   **Entry Zone:** [Price or "Current Market Price"]
*   **Target (TP):** [Price or "Open"]
*   **Stop Loss (SL):** [Price or "N/A"]

### Rationale
[Brief explanation citing specific context using Post [1], Post [2] format based on the tool output.]

---
**Disclaimer:** This is an AI-generated analysis based on social sentiment, not financial advice.

**MODE 2: GENERAL CHAT**
If the user asks a general question (e.g., "What are people saying about AI?", "Summarize the news", "Who is posting?"), simply answer the question clearly and concisely, using information from the `search_user_posts` tool if needed. Cite sources if discussing specific posts. Do NOT use the Trade Strategy format for general questions.

Remember, you do not hallucinate signals. Base your signals on the sentiments found in the retrieved posts. If no relevant posts are found for a ticker, state that you cannot formulate a strategy.
"""
        
        if self.api_key:
            self.llm = ChatOpenAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.2,
                max_tokens=800
            )
            self.agent = create_react_agent(self.llm, self.tools)
        else:
            self.llm = None
            self.agent = None
            
    def invoke(self, question: str) -> str:
        if not self.agent:
            return "LLM service is not configured. Please configure OpenAI API key."
        
        try:
            inputs = {"messages": [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=question)
            ]}
            result = self.agent.invoke(inputs)
            
            # The last message in the output is the AI response
            return result["messages"][-1].content
        except Exception as e:
            logger.error("Failed to execute LangGraph agent", error=str(e))
            return "I encountered an error while generating an answer."
