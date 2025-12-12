import requests
import json

url = 'https://backend.metacritic.com/reviews/metacritic/user/games/animal-crossing-new-horizons/web'
params = {
    'offset': 0,
    'limit': 100,
    'filterBySentiment': 'all',
    'sort': 'date'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.metacritic.com/'
}

print("Testing API endpoint...")
print(f"URL: {url}")
print(f"Params: {params}\n")

response = requests.get(url, params=params, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Response Length: {len(response.text)}")

if response.status_code == 200:
    print("\n=== First 500 characters of response ===")
    print(response.text[:500])

    try:
        data = response.json()
        print("\n=== JSON Structure ===")
        print(f"Top-level keys: {list(data.keys())}")

        if 'data' in data:
            print(f"data keys: {list(data['data'].keys())}")
            print(f"totalResults: {data['data'].get('totalResults')}")
            print(f"Number of items: {len(data['data'].get('items', []))}")

            if data['data'].get('items'):
                print(f"\n=== First review structure ===")
                first_review = data['data']['items'][0]
                for key, value in first_review.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"  {key}: {value[:50]}...")
                    else:
                        print(f"  {key}: {value}")
    except Exception as e:
        print(f"\n❌ Response is not valid JSON: {e}")
        print(response.text)
else:
    print(f"\n❌ Error response:")
    print(response.text[:1000])
