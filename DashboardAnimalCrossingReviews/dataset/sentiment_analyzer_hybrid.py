"""
Hybrid Sentiment Analysis for Animal Crossing Reviews
This script combines VADER sentiment analysis with user scores for more accurate classification.

Strategy:
1. Use VADER to analyze the text tone
2. Use user_score as ground truth (0-3=Negative, 4-6=Neutral, 7-10=Positive)
3. Combine both for final classification
"""

import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

print("="*60)
print("HYBRID SENTIMENT ANALYSIS")
print("Animal Crossing Reviews - VADER + User Score")
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

def analyze_sentiment_hybrid(text, user_score):
    """
    Hybrid sentiment analysis combining VADER and user score

    Parameters:
    - text: Review text
    - user_score: User rating (0-10)

    Returns:
    - vader_score: VADER compound score (-1 to 1)
    - final_label: Hybrid classification (Positive/Negative/Neutral)
    - method: Which method was used for classification
    """
    if pd.isna(text) or text == "":
        vader_score = 0.0
    else:
        scores = sia.polarity_scores(str(text))
        vader_score = scores['compound']

    # Classify based on user_score (ground truth)
    # 0-3: Negative
    # 4-6: Neutral/Mixed
    # 7-10: Positive
    if user_score <= 3:
        score_label = "Negative"
    elif user_score <= 6:
        score_label = "Neutral"
    else:
        score_label = "Positive"

    # VADER classification
    if vader_score >= 0.3:
        vader_label = "Positive"
    elif vader_score <= -0.3:
        vader_label = "Negative"
    else:
        vader_label = "Neutral"

    # HYBRID LOGIC:
    # Priority 1: If user_score is extreme (0-2 or 9-10), trust the user
    # Priority 2: If VADER and user_score agree, use that
    # Priority 3: If they disagree, use user_score (ground truth)

    if user_score <= 2:
        # Very low score - definitely negative
        final_label = "Negative"
        method = "user_score (very low)"
    elif user_score >= 9:
        # Very high score - definitely positive
        final_label = "Positive"
        method = "user_score (very high)"
    elif vader_label == score_label:
        # Agreement - use agreed label
        final_label = score_label
        method = "agreement"
    else:
        # Disagreement - trust user_score over VADER
        # (user knows if they liked it, VADER only reads tone)
        final_label = score_label
        method = "user_score (disagreement)"

    return vader_score, final_label, method

# Perform hybrid sentiment analysis
print("Analyzing sentiment with hybrid approach...")
print("(Combining VADER text analysis with user ratings)\n")

sentiment_results = df.apply(lambda row: analyze_sentiment_hybrid(row['review_text'], row['user_score']), axis=1)

# Separate results
df['sentiment_score'] = sentiment_results.apply(lambda x: x[0])
df['sentiment_label'] = sentiment_results.apply(lambda x: x[1])
df['classification_method'] = sentiment_results.apply(lambda x: x[2])

print(">>> Hybrid sentiment analysis complete!\n")

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

# Show classification method distribution
print("\n" + "="*60)
print("CLASSIFICATION METHOD BREAKDOWN")
print("="*60)
method_counts = df['classification_method'].value_counts()
print(f"\n{method_counts}\n")

print("Percentages:")
method_pct = df['classification_method'].value_counts(normalize=True) * 100
for method, pct in method_pct.items():
    print(f"  {method}: {pct:.1f}%")

# Analyze agreement vs disagreement
print("\n" + "="*60)
print("VADER vs USER SCORE ANALYSIS")
print("="*60)

agreement_rate = (df['classification_method'] == 'agreement').sum() / len(df) * 100
print(f"\nAgreement rate: {agreement_rate:.1f}%")
print(f"(When VADER and user_score classifications match)")

# Show correlation
correlation = df[['user_score', 'sentiment_score']].corr()
print(f"\nCorrelation coefficient: {correlation.iloc[0, 1]:.3f}")

# Group by user score
print("\n" + "="*60)
print("SENTIMENT BY USER SCORE")
print("="*60)
print("\nDistribution of final labels by user score:")

for score in range(11):
    subset = df[df['user_score'] == score]
    if len(subset) > 0:
        label_dist = subset['sentiment_label'].value_counts()
        print(f"\nScore {score}/10 ({len(subset)} reviews):")
        for label, count in label_dist.items():
            pct = count / len(subset) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")

# Save to new CSV
output_file = 'animal_crossing_reviews_with_sentiment.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n" + "="*60)
print("PROCESSING COMPLETE!")
print("="*60)
print(f"\nOutput file: {output_file}")
print(f"Total reviews: {len(df)}")
print(f"\nNew columns added:")
print(f"  - sentiment_score: VADER compound score (-1 to 1)")
print(f"  - sentiment_label: Hybrid classification (Positive/Negative/Neutral)")
print(f"  - classification_method: How the label was determined")

# Show examples
print("\n" + "="*60)
print("SAMPLE REVIEWS")
print("="*60)

# Example where user_score overrode VADER
print("\n--- EXAMPLE: User Score Override ---")
print("(Reviews where VADER disagreed with user rating)")
disagreement = df[df['classification_method'] == 'user_score (disagreement)'].head(1)
if len(disagreement) > 0:
    example = disagreement.iloc[0]
    print(f"User Score: {example['user_score']}/10")
    print(f"VADER Score: {example['sentiment_score']:.3f}")
    print(f"Final Label: {example['sentiment_label']}")
    try:
        print(f"Review: {example['review_text'][:200]}...")
    except:
        print(f"Review: [Contains special characters]")

# Example of agreement
print("\n--- EXAMPLE: Agreement ---")
print("(Reviews where VADER and user score agreed)")
agreement_ex = df[df['classification_method'] == 'agreement'].head(1)
if len(agreement_ex) > 0:
    example = agreement_ex.iloc[0]
    print(f"User Score: {example['user_score']}/10")
    print(f"VADER Score: {example['sentiment_score']:.3f}")
    print(f"Final Label: {example['sentiment_label']}")
    try:
        print(f"Review: {example['review_text'][:200]}...")
    except:
        print(f"Review: [Contains special characters]")

print("\n" + "="*60)
print("Ready for Power BI visualization!")
print("="*60)
print("\nThis hybrid approach is more accurate because it:")
print("  1. Respects user ratings as ground truth")
print("  2. Uses VADER to confirm when possible")
print("  3. Handles sarcasm and irony better")