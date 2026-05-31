from typing import List, Dict


class RelationExtractor:
    def __init__(self):
        self._nlp = None

    @property
    def nlp(self):
        if self._nlp is None:
            import spacy
            from app.config import settings
            self._nlp = spacy.load(settings.spacy_model)
        return self._nlp

    def extract(self, text: str) -> List[Dict]:
        doc = self.nlp(text[:500_000])
        triples = []

        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                subjects = [c for c in token.children if c.dep_ in ("nsubj", "nsubjpass")]
                objects = [c for c in token.children if c.dep_ in ("dobj", "attr", "pobj")]
                for subj in subjects:
                    for obj in objects:
                        triples.append({
                            "subject": subj.text,
                            "predicate": token.lemma_.upper(),
                            "object": obj.text,
                            "evidence": token.sent.text,
                        })

        return triples[:50]  # cap to avoid noise on long documents
