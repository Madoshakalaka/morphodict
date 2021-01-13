from collections import defaultdict
from itertools import chain
from typing import Dict, Iterable, List, Tuple, NewType

import dawg
from utils.cree_lev_dist import remove_cree_diacritics

# A simplified form intended to be used within the affix search trie.
SimplifiedForm = NewType("SimplifiedForm", str)


class AffixSearcher:
    """
    Enables prefix and suffix searches given a list of words and their wordform IDs.
    """

    # TODO: "int" should be Wordform PK type
    # TODO: "str" should be InternalForm

    def __init__(self, words: List[Tuple[str, int]]):
        self.text_to_ids: Dict[str, List[int]] = defaultdict(list)

        words_marked_for_indexing = [
            (simplified_text, wordform_id)
            for raw_text, wordform_id in words
            if (simplified_text := self.to_simplified_form(raw_text))
        ]

        for text, wordform_id in words_marked_for_indexing:
            self.text_to_ids[self.to_simplified_form(text)].append(wordform_id)

        self._prefixes = dawg.CompletionDAWG(
            [text for text, _ in words_marked_for_indexing]
        )
        self._suffixes = dawg.CompletionDAWG(
            [text[::-1] for text, _ in words_marked_for_indexing]
        )

    def search_by_prefix(self, prefix: str) -> Iterable[int]:
        """
        :return: an iterable of ids
        """
        # lower & remove diacritics
        prefix = self.to_simplified_form(prefix)
        return chain(*[self.text_to_ids[t] for t in self._prefixes.keys(prefix)])

    def search_by_suffix(self, suffix: str) -> Iterable[int]:
        """
        :return: an iterable of ids
        """
        # lower & remove diacritics
        suffix = self.to_simplified_form(suffix)

        return chain(
            *[self.text_to_ids[x[::-1]] for x in self._suffixes.keys(suffix[::-1])]
        )

    # TODO: return type should be InternalForm
    @staticmethod
    def to_simplified_form(query: str) -> SimplifiedForm:
        """
        Convert to a simplified form of the word and its orthography to facilitate affix
        search.  You SHOULD throw out diacritics, choose a Unicode Normalization form,
        and choose a single letter case here!
        """
        # TODO: make this work for not just Cree!
        return remove_cree_diacritics(query.lower())
