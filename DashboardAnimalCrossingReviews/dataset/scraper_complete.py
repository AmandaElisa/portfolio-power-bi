"""
Metacritic API Scraper - Animal Crossing: New Horizons
This scraper uses Metacritic's internal API to collect user reviews.
"""

import requests
import pandas as pd
from time import sleep
import json

def scrape_metacritic_api(max_reviews=None):
    """
    Scrape user reviews using Metacritic's internal API

    Parameters:
    -----------
    max_reviews : int, optional
        Maximum number of reviews to collect. If None, gets all available.

    Returns:
    --------
    pd.DataFrame
        DataFrame with all collected reviews
    """

    base_url = 'https://backend.metacritic.com/reviews/metacritic/user/games/animal-crossing-new-horizons/web'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.metacritic.com/'
    }

    all_reviews = []
    offset = 0
    limit = 100  # Max per request
    total_results = None

    print("Starting API scraping...\n")

    while True:
        # Check if we've reached max_reviews
        if max_reviews and len(all_reviews) >= max_reviews:
            print(f"\nReached max_reviews limit ({max_reviews})")
            break

        # Build URL with parameters
        params = {
            'offset': offset,
            'limit': limit,
            'filterBySentiment': 'all',
            'sort': 'date'
        }

        print(f"Fetching reviews {offset}-{offset + limit}...", end=' ')

        try:
            response = requests.get(base_url, params=params, headers=headers)

            if response.status_code != 200:
                print(f"\nError: Status {response.status_code}")
                print(f"Response: {response.text[:500]}")
                break

            data = response.json()

            # Get total results from first request
            if total_results is None:
                if 'data' in data and 'totalResults' in data['data']:
                    total_results = data['data']['totalResults']
                    print(f"\n>>> Total reviews available: {total_results}\n")
                    print(f"Fetching reviews {offset}-{offset + limit}...", end=' ')

            # Check if there are reviews in the response
            if 'data' not in data:
                print(f"No 'data' key in response! Keys: {list(data.keys())}")
                break

            if 'items' not in data['data']:
                print(f"No 'items' key in data! Keys: {list(data['data'].keys())}")
                break

            reviews = data['data']['items']

            if len(reviews) == 0:
                print("No more reviews!")
                break

            print(f">>> Got {len(reviews)} reviews")

            # Extract data from each review
            for review in reviews:
                review_data = {
                    'username': review.get('author', 'Anonymous'),
                    'user_score': review.get('score', None),
                    'review_date': review.get('date', None),
                    'review_text': review.get('quote', None),
                    'thumbs_up': review.get('thumbsUp', None),
                    'thumbs_down': review.get('thumbsDown', None),
                    'platform': review.get('platform', 'Nintendo Switch')
                }
                all_reviews.append(review_data)

            # If we got fewer reviews than limit, we've reached the end
            if len(reviews) < limit:
                print("\n>>> Reached end of available reviews!")
                break

            offset += limit

            # Small delay to be respectful
            sleep(0.5)

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            break

    print(f"\n{'='*60}")
    print(f">>> Total reviews collected: {len(all_reviews)}")
    if total_results:
        print(f">>> Out of {total_results} total available")
        percentage = (len(all_reviews) / total_results * 100)
        print(f">>> Success rate: {percentage:.1f}%")
    print(f"{'='*60}\n")

    return pd.DataFrame(all_reviews)


if __name__ == "__main__":
    # Collect all reviews
    print("="*60)
    print("METACRITIC API SCRAPER")
    print("Animal Crossing: New Horizons - User Reviews")
    print("="*60 + "\n")

    df_reviews = scrape_metacritic_api()

    if len(df_reviews) > 0:
        print("\n" + "="*60)
        print("DATA ANALYSIS")
        print("="*60)

        print(f"\nTotal reviews: {len(df_reviews)}")
        print(f"\nScore distribution:")
        print(df_reviews['user_score'].value_counts().sort_index())

        print(f"\nStatistics:")
        print(df_reviews.describe())

        print(f"\nData quality:")
        print(f"  Reviews with username: {df_reviews['username'].notna().sum()}")
        print(f"  Reviews with score: {df_reviews['user_score'].notna().sum()}")
        print(f"  Reviews with text: {df_reviews['review_text'].notna().sum()}")
        print(f"  Reviews with date: {df_reviews['review_date'].notna().sum()}")

        # Export to CSV
        filename = 'animal_crossing_reviews_full.csv'
        df_reviews.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n{'='*60}")
        print(f">>> Saved {len(df_reviews)} reviews to '{filename}'!")
        print(f"{'='*60}")

        print(f"\n=== First 5 reviews ===")
        print(df_reviews.head())
    else:
        print("ERROR: No data collected")
