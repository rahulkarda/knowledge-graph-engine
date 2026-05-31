from typing import List, Dict
from collections import Counter


STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
               "have", "has", "had", "do", "does", "did", "will", "would", "could",
               "should", "may", "might", "this", "that", "these", "those", "it",
               "its", "and", "or", "but", "in", "on", "at", "to", "for", "of",
               "with", "by", "from", "up", "about", "into", "through", "i", "you",
               "he", "she", "we", "they", "my", "your", "our", "their"}


class AutoTagger:
    def suggest(self, text: str, entities: List[Dict], max_tags: int = 5) -> List[str]:
        tags = set()

        # High-confidence tags from named entities (PERSON, ORG, GPE)
        for e in entities:
            if e["entity_type"] in ("PERSON", "ORG", "GPE", "LOC") and len(e["name"].split()) <= 3:
                tags.add(e["name"].lower())

        # Keyword frequency fallback
        words = [w.lower() for w in text.split() if len(w) > 4 and w.lower() not in STOP_WORDS and w.isalpha()]
        freq = Counter(words)
        for word, _ in freq.most_common(10):
            if len(tags) >= max_tags:
                break
            tags.add(word)

        return list(tags)[:max_tags]
