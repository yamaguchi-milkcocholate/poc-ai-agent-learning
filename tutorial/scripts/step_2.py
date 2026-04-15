import os

import requests
from dotenv import load_dotenv
from langchain_community.tools.ddg_search import DuckDuckGoSearchRun
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


class WeatherArgs(BaseModel):
    lat: float = Field(..., description="緯度")
    lon: float = Field(..., description="経度")


@tool(args_schema=WeatherArgs)
def open_meteo_weather(lat: float, lon: float) -> str:
    """Open-Meteoから今日の時間別気温(℃)を取得し要約する。APIキー不要。"""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}&hourly=temperature_2m&forecast_days=1"
    )
    data = requests.get(url, timeout=20).json()
    temps = data["hourly"]["temperature_2m"][:6]
    return f"最初の6時間の気温: {temps}"


# 1) LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2) 無料検索ツール（日本語にバイアス）
ddg_api = DuckDuckGoSearchAPIWrapper(
    region="jp-jp", safesearch="moderate", backend="api"
)
ddg_tool = DuckDuckGoSearchRun(api_wrapper=ddg_api)

# 3) 自作ツール（上で定義した open_meteo_weather）を追加
tools = [ddg_tool, open_meteo_weather]

# 4) チェックポイント（thread_id単位で状態保持）
memory = MemorySaver()
agent = create_react_agent(llm, tools, checkpointer=memory)
cfg = {"configurable": {"thread_id": "step2-demo"}}

# 例：東京駅付近の天気を取りつつ、LangGraphドキュメントも参照
q1 = "東京(35.681, 139.767)の今日の気温を簡単に。参考リンクも1つ。"
print(agent.invoke({"messages": [("user", q1)]}, cfg)["messages"][-1].content)

# ストリーミングで推論/ツール実行の流れを確認したい場合
for chunk in agent.stream(
    {"messages": [("user", "LangGraphのprebuilt ReActの要点を3つ")]},
    cfg,
    stream_mode="values",
):
    msg = chunk["messages"][-1]
    print(getattr(msg, "content", msg))
