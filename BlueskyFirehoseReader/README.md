# Bluesky Jetstream Tutorial: Filtering Political Content with Sentiment Analysis

This tutorial walks you through using Jetstream (Bluesky Firehose) to extract and analyze political posts in English with positive sentiment. We will:

1. Filter for English-language posts  
2. Select political content using keyword matching  
3. Apply sentiment analysis using VADER to retain only positively scored posts

---

## Step 1: Select Posts in English

Jetstream delivers posts from all languages. To filter for English:

```python
if "en" in record.get("langs", []):
    # proceed
```

---

## Step 2: Match Political Keywords

Define a list of political keywords and retain posts containing at least one keyword. Use a case-insensitive match.

```python
political_keywords = [
    "trump",
    "immigration",
    "vote",
    "democrat",
    "republican",
    "congress",
    "senate",
    "gop",
    "tariffs",
    "president"
]

def is_political(text):
    lowered = text.lower()
    return any(kw in lowered for kw in political_keywords)
```

---

## Step 3: Sentiment Analysis with VADER

Install `vaderSentiment` if you haven’t already:

```bash
pip install vaderSentiment
```

Then use it to compute sentiment scores:

```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
...


sentiment = analyzer.polarity_scores(text)
if sentiment["compound"] > 0.5:
    # retain post
```

### Example

```python
example_text = "I believe the president made a great decision today."
sentiment = analyzer.polarity_scores(example_text)
print(sentiment)  # Output: {'neg': 0.0, 'neu': 0.507, 'pos': 0.493, 'compound': 0.6249}
```

Since the `compound` score is greater than 0.5, this post would be included.
