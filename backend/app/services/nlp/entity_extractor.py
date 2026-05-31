import re
from typing import List, Dict

# Patterns that identify common entity types without needing spaCy
_PERSON_HINTS = re.compile(
    r'\b(by|from|author|wrote|created|invented|founded by|named)\s+([A-Z][a-z]+ (?:[A-Z][a-z]+ )?[A-Z][a-z]+)',
    re.IGNORECASE,
)
_PROPER_NOUN = re.compile(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b')
_URL_PATTERN = re.compile(r'https?://\S+')

# Common words to exclude from entity extraction
_STOPWORDS = {
    "the", "this", "that", "these", "those", "then", "they", "them", "their",
    "there", "here", "when", "what", "which", "who", "how", "why", "where",
    "and", "but", "for", "with", "not", "from", "also", "into", "each",
    "have", "been", "some", "such", "will", "more", "very", "just", "can",
    "one", "two", "three", "may", "its", "than", "our", "your", "my",
    "was", "are", "is", "be", "been", "has", "had", "do", "did", "does",
    "i", "we", "he", "she", "it", "a", "an", "in", "on", "at", "to", "of",
    "want", "like", "love", "know", "go", "use", "get", "make", "take",
    "before", "after", "during", "about", "between", "through",
    "morning", "evening", "night", "day", "week", "month", "year",
    "minutes", "hours", "times", "people", "things", "way", "ways",
    "favorite", "favourite",
}

KEPT_ENTITY_TYPES = {"PERSON", "ORG", "GPE", "LOC", "EVENT", "CONCEPT", "WORK_OF_ART"}


class EntityExtractor:
    def __init__(self):
        self._nlp = None
        self._spacy_available = None

    def _try_load_spacy(self):
        if self._spacy_available is not None:
            return self._spacy_available
        try:
            import spacy
            from app.config import settings
            self._nlp = spacy.load(settings.spacy_model)
            self._spacy_available = True
        except Exception:
            self._spacy_available = False
        return self._spacy_available

    def extract(self, text: str) -> List[Dict]:
        if self._try_load_spacy():
            return self._extract_spacy(text)
        return self._extract_regex(text)

    def _extract_spacy(self, text: str) -> List[Dict]:
        doc = self._nlp(text[:1_000_000])
        entities = []
        seen = set()

        for ent in doc.ents:
            if ent.label_ not in KEPT_ENTITY_TYPES:
                continue
            canonical = ent.text.strip().lower()
            if canonical in seen or len(canonical) < 2:
                continue
            seen.add(canonical)
            entities.append({
                "name": ent.text.strip(),
                "entity_type": ent.label_,
                "canonical_name": canonical,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
            })

        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:
                canonical = chunk.text.strip().lower()
                if canonical not in seen and len(canonical) > 3:
                    seen.add(canonical)
                    entities.append({
                        "name": chunk.text.strip(),
                        "entity_type": "CONCEPT",
                        "canonical_name": canonical,
                        "start_char": chunk.start_char,
                        "end_char": chunk.end_char,
                    })
        return entities

    def _extract_regex(self, text: str) -> List[Dict]:
        entities = []
        seen = set()

        # Remove URLs before processing
        clean_text = _URL_PATTERN.sub("", text)

        # Named author extraction (e.g. "by James Clear")
        for m in _PERSON_HINTS.finditer(clean_text):
            name = m.group(2).strip()
            canonical = name.lower()
            if canonical not in seen:
                seen.add(canonical)
                entities.append({
                    "name": name,
                    "entity_type": "PERSON",
                    "canonical_name": canonical,
                    "start_char": m.start(2),
                    "end_char": m.end(2),
                })

        # Proper nouns (Title Case sequences) as general entities
        for m in _PROPER_NOUN.finditer(clean_text):
            name = m.group(1).strip()
            canonical = name.lower()
            words = canonical.split()
            # Skip single common words and stopwords
            if len(words) == 1 and canonical in _STOPWORDS:
                continue
            if canonical in seen or len(canonical) < 3:
                continue
            # Skip if already captured as a person
            if any(canonical in e["canonical_name"] for e in entities):
                continue
            seen.add(canonical)
            # Classify heuristically
            entity_type = _classify(name, clean_text)
            entities.append({
                "name": name,
                "entity_type": entity_type,
                "canonical_name": canonical,
                "start_char": m.start(),
                "end_char": m.end(),
            })

        return entities[:30]  # cap to avoid noise


def _classify(name: str, context: str) -> str:
    """Rough heuristic classification for a proper noun."""
    countries_cities = {
        "japan", "iceland", "new zealand", "india", "usa", "uk", "france",
        "germany", "australia", "canada", "china", "brazil", "london",
        "paris", "tokyo", "new york", "berlin", "sydney",
    }
    if name.lower() in countries_cities:
        return "GPE"
    # Multi-word with title-like words → WORK_OF_ART
    if len(name.split()) >= 2 and any(w in context.lower() for w in ["book", "novel", "film", "series", "album"]):
        return "WORK_OF_ART"
    return "CONCEPT"
