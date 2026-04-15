import os

from dotenv import load_dotenv
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# 1) LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

# 2) 無料ツール（DuckDuckGo 検索）
ddg_api = DuckDuckGoSearchAPIWrapper(
    region="jp-jp",  # ← ここを変更
    safesearch="moderate",  # 任意: strict/moderate/off
    backend="api",  # 任意: api/html/lite
    time="y",  # 任意: d/w/m/y
)
ddg_tool = DuckDuckGoSearchRun(api_wrapper=ddg_api)

# 3) メモリ（チェックポイント）
memory = MemorySaver()

# 4) ReAct エージェント（LangGraph の推奨プリビルト）
agent = create_react_agent(model=llm, tools=[ddg_tool], checkpointer=memory)

# 5) thread_id を固定すると会話文脈が続く
cfg = {"configurable": {"thread_id": "demo-ddg-001"}}

# 実行例1：検索を要する質問
res1 = agent.invoke(
    {
        "messages": [
            (
                "user",
                "LangGraph の prebuilt ReAct エージェントのドキュメントURLを教えて。",
            )
        ]
    },
    cfg,
)
print(res1["messages"][-1].content)

# 実行例2：前の結果を踏まえたフォローアップ
res2 = agent.invoke({"messages": [("user", "さっき教えてくれたURLの要点を3行で")]}, cfg)
print(res2["messages"][-1].content)
