"""
NLP Text Cleaner for Animal Crossing Reviews
This script performs text cleaning and preprocessing for Power BI word cloud visualization.

Steps:
1. Load CSV with reviews
2. Clean text (lowercase, remove punctuation, special characters)
3. Lemmatize using spaCy
4. Remove stopwords (except important negations)
5. Create new columns:
   - review_clean: Sanitized text
   - words_for_wordcloud: Space-separated words without stopwords
"""

import pandas as pd
import string
import re
import nltk
from nltk.corpus import stopwords

print("="*60)
print("NLP TEXT CLEANER")
print("Animal Crossing Reviews - Text Preprocessing")
print("="*60 + "\n")

# Download NLTK stopwords
print("Downloading NLTK stopwords...")
try:
    nltk.download('stopwords', quiet=True)
    print(">>> Stopwords downloaded!\n")
except:
    print(">>> Stopwords already available!\n")

# Try to import spacy
try:
    import spacy
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")
    print(">>> spaCy model loaded!\n")
    USE_SPACY = True
except:
    print("WARNING: spaCy not available. Will use basic text cleaning without lemmatization.")
    print("To enable lemmatization, install: pip install spacy")
    print("Then download model: python -m spacy download en_core_web_sm\n")
    USE_SPACY = False

# Load CSV
print("Loading CSV file...")
input_file = 'animal_crossing_reviews_full.csv'
df = pd.read_csv(input_file, encoding='utf-8-sig')
print(f">>> Loaded {len(df)} reviews\n")

# Prepare stopwords
print("Preparing stopwords list...")
stop_words = stopwords.words('english')

# Remove important negations that should be kept
negations_to_keep = ['no', 'not', 'don', 'don\'t', 'dont', 'couldn', 'couldn\'t', 'couldnt', 'won', 'won\'t', 'wont']
for word in negations_to_keep:
    if word in stop_words:
        stop_words.remove(word)

print(f">>> Using {len(stop_words)} stopwords (keeping negations: {negations_to_keep[:4]}...)\n")

def clean_text(text):
    """
    Clean text by:
    - Converting to lowercase
    - Removing URLs
    - Removing special characters and emojis
    - Removing extra whitespace
    """
    if pd.isna(text):
        return ""

    # Convert to string and lowercase
    text = str(text).lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)

    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove emojis and special characters (keep letters, numbers, spaces, and basic punctuation)
    text = re.sub(r'[^\w\s\'\-]', ' ', text)

    # Remove digits
    text = re.sub(r'\d+', '', text)

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text

def lemmatize_text(text):
    """Lemmatize text using spaCy"""
    if not USE_SPACY or not text:
        return text

    doc = nlp(text)
    lemmatized = ' '.join([token.lemma_ if token.lemma_ != "-PRON-" else token.text for token in doc])
    return lemmatized

def remove_stopwords(text, stopwords_list):
    """Remove stopwords from text"""
    if not text:
        return ""

    words = text.split()
    filtered_words = [word for word in words if word not in stopwords_list and len(word) > 1]
    return ' '.join(filtered_words)

# Process reviews
print("Processing reviews...")
print("Step 1: Cleaning text...")
df['review_clean'] = df['review_text'].apply(clean_text)
print(">>> Text cleaned!\n")

if USE_SPACY:
    print("Step 2: Lemmatizing text (this may take a few minutes)...")
    df['review_clean'] = df['review_clean'].apply(lemmatize_text)
    print(">>> Text lemmatized!\n")
else:
    print("Step 2: Skipping lemmatization (spaCy not available)\n")

print("Step 3: Creating wordcloud column (removing stopwords)...")
df['words_for_wordcloud'] = df['review_clean'].apply(lambda x: remove_stopwords(x, stop_words))
print(">>> Wordcloud column created!\n")

# Save to new CSV
output_file = 'animal_crossing_reviews_processed.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("="*60)
print("PROCESSING COMPLETE!")
print("="*60)
print(f"\nOutput file: {output_file}")
print(f"Total reviews: {len(df)}")
print(f"\nNew columns added:")
print(f"  - review_clean: Sanitized and lemmatized text")
print(f"  - words_for_wordcloud: Words without stopwords for Power BI")

# Show statistics
print(f"\nSample data:")
print("="*60)
for idx, row in df.head(3).iterrows():
    print(f"\nReview #{idx+1}:")
    print(f"Original: {row['review_text'][:100]}...")
    print(f"Cleaned:  {row['review_clean'][:100]}...")
    print(f"Wordcloud: {row['words_for_wordcloud'][:100]}...")

print("\n" + "="*60)
print("Ready for Power BI!")
print("="*60)
