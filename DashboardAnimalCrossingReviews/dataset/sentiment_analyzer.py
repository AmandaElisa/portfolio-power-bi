"""
Sentiment Analysis for Animal Crossing Reviews
This script performs sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner).

VADER is specifically attuned to sentiments expressed in social media and works well for:
- Game reviews
- Social media posts
- Short texts with slang and emoticons

Output:
- sentiment_score: Compound score (-1 to 1)
- sentiment_label: Positive/Negative/Neutral
"""

import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

print("="*60)
print("SENTIMENT ANALYSIS")
print("Animal Crossing Reviews - VADER Sentiment Analyzer")
print("="*60 + "\n")

# Download VADER lexicon
print("Downloading VADER lexicon...")
try:
    nltk.download('vader_lexicon', quiet=True)
    print(">>> VADER lexicon downloaded!\n")
except:
    print(">>> VADER lexicon already available!\n")

# Initialize VADER
print("Initializing VADER sentiment analyzer...")
sia = SentimentIntensityAnalyzer()
print(">>> VADER initialized!\n")

# Load processed CSV
print("Loading processed CSV file...")
input_file = 'animal_crossing_reviews_processed.csv'
df = pd.read_csv(input_file, encoding='utf-8-sig')
print(f">>> Loaded {len(df)} reviews\n")

def analyze_sentiment(text):
    """
    Analyze sentiment using VADER

    Returns:
    - compound: Overall sentiment score (-1 to 1)
    - label: Positive/Negative/Neutral
    """
    if pd.isna(text) or text == "":
        return 0.0, "Neutral"

    # Get sentiment scores
    scores = sia.polarity_scores(str(text))
    compound = scores['compound']

    # Classify sentiment based on compound score
    # Using stricter thresholds for more accurate classification:
    # - Positive: >= 0.3 (clearly positive)
    # - Negative: <= -0.3 (clearly negative)
    # - Neutral: between -0.3 and 0.3 (mixed or neutral)
    if compound >= 0.3:
        label = "Positive"
    elif compound <= -0.3:
        label = "Negative"
    else:
        label = "Neutral"

    return compound, label

# Perform sentiment analysis
print("Analyzing sentiment for all reviews...")
print("(This uses the original review text for more accurate results)\n")

# Use original review_text for sentiment analysis (more accurate than cleaned text)
sentiment_results = df['review_text'].apply(analyze_sentiment)

# Separate compound scores and labels
df['sentiment_score'] = sentiment_results.apply(lambda x: x[0])
df['sentiment_label'] = sentiment_results.apply(lambda x: x[1])

print(">>> Sentiment analysis complete!\n")

# Calculate statistics
print("="*60)
print("SENTIMENT DISTRIBUTION")
print("="*60)
sentiment_counts = df['sentiment_label'].value_counts()
print(f"\n{sentiment_counts}\n")

print("Percentages:")
sentiment_pct = df['sentiment_label'].value_counts(normalize=True) * 100
for label, pct in sentiment_pct.items():
    print(f"  {label}: {pct:.1f}%")

print(f"\nAverage sentiment score: {df['sentiment_score'].mean():.3f}")
print(f"  (Range: -1.0 = Very Negative, +1.0 = Very Positive)")

# Compare sentiment with user scores
print("\n" + "="*60)
print("SENTIMENT vs USER SCORE CORRELATION")
print("="*60)

correlation = df[['user_score', 'sentiment_score']].corr()
print(f"\nCorrelation coefficient: {correlation.iloc[0, 1]:.3f}")
print("(1.0 = Perfect positive correlation, -1.0 = Perfect negative correlation)")

# Group by user score and show average sentiment
print("\nAverage sentiment by user score:")
score_sentiment = df.groupby('user_score')['sentiment_score'].mean().sort_index()
for score, sentiment in score_sentiment.items():
    sentiment_label = "Positive" if sentiment >= 0.05 else ("Negative" if sentiment <= -0.05 else "Neutral")
    print(f"  Score {int(score):2d}: {sentiment:+.3f} ({sentiment_label})")

# Save to new CSV
output_file = 'animal_crossing_reviews_with_sentiment.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n" + "="*60)
print("PROCESSING COMPLETE!")
print("="*60)
print(f"\nOutput file: {output_file}")
print(f"Total reviews: {len(df)}")
print(f"\nNew columns added:")
print(f"  - sentiment_score: Compound sentiment score (-1 to 1)")
print(f"  - sentiment_label: Positive/Negative/Neutral classification")

# Show examples
print("\n" + "="*60)
print("SAMPLE REVIEWS BY SENTIMENT")
print("="*60)

# Most positive
print("\n--- MOST POSITIVE REVIEW ---")
most_positive = df.loc[df['sentiment_score'].idxmax()]
print(f"Score: {most_positive['sentiment_score']:.3f}")
print(f"User Rating: {most_positive['user_score']}/10")
try:
    print(f"Review: {most_positive['review_text'][:200]}...")
except:
    print(f"Review: [Contains special characters]")

# Most negative
print("\n--- MOST NEGATIVE REVIEW ---")
most_negative = df.loc[df['sentiment_score'].idxmin()]
print(f"Score: {most_negative['sentiment_score']:.3f}")
print(f"User Rating: {most_negative['user_score']}/10")
try:
    print(f"Review: {most_negative['review_text'][:200]}...")
except:
    print(f"Review: [Contains special characters]")

# Neutral example
print("\n--- NEUTRAL REVIEW EXAMPLE ---")
neutral = df[df['sentiment_label'] == 'Neutral'].iloc[0] if len(df[df['sentiment_label'] == 'Neutral']) > 0 else None
if neutral is not None:
    print(f"Score: {neutral['sentiment_score']:.3f}")
    print(f"User Rating: {neutral['user_score']}/10")
    try:
        print(f"Review: {neutral['review_text'][:200]}...")
    except:
        print(f"Review: [Contains special characters]")

print("\n" + "="*60)
print("Ready for Power BI visualization!")
print("="*60)
print("\nYou can now use 'sentiment_label' and 'sentiment_score'")
print("to create visualizations in Power BI!")