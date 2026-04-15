import os
from pprint import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GOOGLE_MAP_API_KEY")
BASE = "https://places.googleapis.com/v1"
HEADERS_BASIC = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": (
        # --- 基本情報 ---
        "places.id,"  # 場所のユニークID（Place Details/Photos取得のキー）
        "places.displayName,"  # 表示名（施設名・店舗名）
        "places.formattedAddress,"  # 整形済み住所（ユーザー向け表示用）
        "places.location,"  # 緯度・経度（地図や距離計算に利用）
        # --- 評価系 ---
        "places.rating,"  # 平均星評価（1.0〜5.0）
        "places.userRatingCount,"  # レビュー件数（評価の信頼度指標）
        # --- 分類・価格 ---
        "places.primaryType,"  # 施設の主要カテゴリ（例: restaurant, tourist_attraction）
        "places.priceLevel,"  # 価格帯（0=無料〜4=とても高い）
        # --- 営業時間 ---
        "places.currentOpeningHours,"  # 現在の営業時間（営業中か、曜日ごとの時間）
        # --- 写真 ---
        "places.photos,"  # 写真メタ情報（Photo ID, サイズ, 出典表記）
        # --- ページング ---
        "nextPageToken"  # 次ページ取得用トークン（Search系のみ）
    ),
}


def text_search(
    query: str,
    page_token: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    radius: int = None,
):
    url = f"{BASE}/places:searchText"
    payload = {
        "textQuery": query,
        "pageSize": 10,
        "languageCode": "ja",
        "regionCode": "JP",
    }
    if page_token:
        payload["pageToken"] = page_token
    if latitude and longitude and radius:
        payload["locationBias"] = (
            {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius,
                }
            },
        )
    r = requests.post(url, headers=HEADERS_BASIC, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


page1 = text_search("野毛 飲み屋")
pprint(page1)
