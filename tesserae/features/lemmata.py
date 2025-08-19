# from cltk.semantics.latin.lookup import Lemmata

"""Utility to provide language specific lemmatizers.

This module adapts the CLTK lemmatizer APIs to the interface expected by
Tesserae.  Older versions of Tesserae relied on the ``Lemmata`` class from
``cltk`` which exposed a ``lookup`` method.  Modern versions of CLTK use
backoff lemmatizers which implement ``lemmatize``.  The :class:`LemmataWrapper`
below wraps whichever lemmatizer is available and provides a ``lookup`` method
returning ``(token, [(lemma, '')])`` tuples so the rest of the code base can
remain unchanged.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

try:  # CLTK >= 1.0
    from cltk.lemmatize.grc import GreekBackoffLemmatizer
    from cltk.lemmatize.lat import LatinBackoffLemmatizer

    class LemmataWrapper:
        def __init__(self, language: str) -> None:
            if language == "latin":
                self.lemmatizer = LatinBackoffLemmatizer()
            elif language == "greek":
                self.lemmatizer = GreekBackoffLemmatizer()
            else:
                raise ValueError(f"Unsupported language: {language}")

        def lookup(
            self, tokens: Iterable[str]
        ) -> List[Tuple[str, List[Tuple[str, str]]]]:
            if not isinstance(tokens, list):
                tokens = [tokens]
            lemmas = self.lemmatizer.lemmatize(tokens)
            return [(tok, [(lemma, "")]) for tok, lemma in lemmas]

except ModuleNotFoundError:  # pragma: no cover - legacy CLTK < 1.0
    from cltk.stem.lemma import LemmaReplacer

    class LemmataWrapper:  # type: ignore[no-redef]
        def __init__(self, language: str) -> None:
            self.lemmatizer = LemmaReplacer(language)

        def lookup(
            self, tokens: Iterable[str]
        ) -> List[Tuple[str, List[Tuple[str, str]]]]:
            if not isinstance(tokens, list):
                tokens = [tokens]
            lemmas = self.lemmatizer.lemmatize(tokens)
            return [(tok, [(lemma, "")]) for tok, lemma in zip(tokens, lemmas)]


# _LEM_MAPPER = {"latin": Lemmata("lemmata", "lat"), "greek": Lemmata("lemmata", "grc")}
_LEM_MAPPER = {
    "latin": LemmataWrapper("latin"),
    "greek": LemmataWrapper("greek"),
}


def get_lemmatizer(language):
    return _LEM_MAPPER[language]
