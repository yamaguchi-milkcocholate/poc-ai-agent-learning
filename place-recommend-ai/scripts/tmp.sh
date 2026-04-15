curl -sX POST "https://places.googleapis.com/v1/places:searchText" \
  -H "Content-Type: application/json" \
  -H "X-Goog-Api-Key: $GOOGLE_MAP_API_KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,nextPageToken" \
  -d '{"textQuery":"横浜 野毛 飲み屋","pageSize":10,"languageCode":"ja","regionCode":"JP"}'
