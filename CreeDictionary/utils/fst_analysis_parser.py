import csv
import re
from enum import IntEnum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO, Tuple

from utils.enums import SimpleLexicalCategory
from utils.types import FSTLemma, FSTTag, Label

from .shared_res_dir import shared_res_dir

analysis_pattern = re.compile(
    r"(?P<category>\+N\+A(\+D(?=\+))?|\+N\+I(\+D(?=\+))?|\+V\+AI|\+V\+T[AI]|\+V\+II|(\+Num)?\+Ipc|\+Pron).*?$"
)


class LabelFriendliness(IntEnum):
    LINGUISTIC_SHORT = auto()
    LINGUISTIC_LONG = auto()
    ENGLISH = auto()
    NEHIYAWEWIN = auto()


class Relabelling(Dict[FSTTag, Dict[LabelFriendliness, Optional[Label]]]):
    def __init__(
        self, data: Dict[FSTTag, Dict[LabelFriendliness, Optional[Label]]]
    ) -> None:
        self._data = data

        self.linguistic_short = _RelabelFetcher(
            data, LabelFriendliness.LINGUISTIC_SHORT
        )
        self.linguistic_long = _RelabelFetcher(data, LabelFriendliness.LINGUISTIC_LONG)
        self.english = _RelabelFetcher(data, LabelFriendliness.ENGLISH)
        self.cree = _RelabelFetcher(data, LabelFriendliness.NEHIYAWEWIN)

    def get(self, key, optional=None):
        return self._data.get(key, optional)

    def __getitem__(self, key: FSTTag) -> Dict[LabelFriendliness, Optional[Label]]:
        return self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    @classmethod
    def from_tsv(cls, csvfile: TextIO) -> "Relabelling":
        res: Dict[FSTTag, Dict[LabelFriendliness, Optional[Label]]] = {}
        reader = csv.reader(csvfile, delimiter="\t")
        for row in list(reader)[1:]:
            if any(row):
                # todo: emojis are not used for now. USE THEM
                tag_dict: Dict[LabelFriendliness, Optional[Label]] = {
                    LabelFriendliness.LINGUISTIC_SHORT: None,
                    LabelFriendliness.LINGUISTIC_LONG: None,
                    LabelFriendliness.ENGLISH: None,
                    LabelFriendliness.NEHIYAWEWIN: None,
                }
                try:
                    fst_tag = row[0]
                    short = row[1]
                    tag_dict[LabelFriendliness.LINGUISTIC_SHORT] = Label(short)
                    long = row[2]
                    tag_dict[LabelFriendliness.LINGUISTIC_LONG] = Label(long)
                    english = row[3]
                    tag_dict[LabelFriendliness.ENGLISH] = Label(english)
                    nihiyawewin = row[4]
                    tag_dict[LabelFriendliness.NEHIYAWEWIN] = Label(nihiyawewin)
                    emoji = row[5]
                except IndexError:  # some of them do not have that many columns
                    pass
                res[FSTTag(fst_tag)] = tag_dict

        return cls(res)


class _RelabelFetcher:
    def __init__(
        self,
        data: Dict[FSTTag, Dict[LabelFriendliness, Optional[Label]]],
        label: LabelFriendliness,
    ):
        self._data = data
        self._label = label

    def __getitem__(self, key: FSTTag) -> Optional[Label]:
        return self._data[key][self._label]

    # TODO: correct type signature
    def get(self, key: FSTTag, default: Any = None) -> Any:
        return self._data.get(key, {}).get(self._label, default)


def read_labels() -> Dict[FSTTag, Dict[LabelFriendliness, Optional[Label]]]:
    with (shared_res_dir / "crk.altlabel.tsv").open(encoding="UTF-8") as csvfile:
        return Relabelling.from_tsv(csvfile)


FST_TAG_LABELS = Relabelling(read_labels())


def partition_analysis(analysis: str) -> Tuple[List[FSTTag], FSTLemma, List[FSTTag]]:
    """
    :return: the tags before the lemma, the lemma itself, the tags after the lemma
    :raise ValueError: when the analysis is not parsable.

    >>> partition_analysis('PV/e+fakeword+N+I')
    (['PV/e'], 'fakeword', ['N', 'I'])
    >>> partition_analysis('fakeword+N+I')
    ([], 'fakeword', ['N', 'I'])
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:

        group = res.group("category")
        if group:
            end = res.span("category")[0]
            cursor = end - 1

            while cursor > 0 and analysis[cursor] != "+":
                cursor -= 1
            if analysis[cursor] == "+":
                cursor += 1

            return (
                [FSTTag(t) for t in analysis[: cursor - 1].split("+")]
                if cursor > 1
                else [],
                FSTLemma(analysis[cursor:end]),
                [FSTTag(t) for t in analysis[end + 1 :].split("+")],
            )
    raise ValueError(f"analysis not parsable: {analysis}")


def extract_lemma(analysis: str) -> Optional[FSTLemma]:
    res = re.search(analysis_pattern, analysis)
    if res is not None:

        group = res.group("category")
        if group:
            end = res.span("category")[0]
            # print(res.groups())
            cursor = end - 1

            while cursor > 0 and analysis[cursor] != "+":
                cursor -= 1
            if analysis[cursor] == "+":
                cursor += 1
            # print(cursor, end)
            return FSTLemma(analysis[cursor:end])
        else:
            return None
    else:
        return None


def extract_lemma_and_category(
    analysis: str,
) -> Optional[Tuple[FSTLemma, SimpleLexicalCategory]]:
    """
    less overhead than calling `extract_lemma` and `extract_simple_lc` separately
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:

        group = res.group("category")
        if group:
            end = res.span("category")[0]
            # print(res.groups())
            cursor = end - 1

            while cursor > 0 and analysis[cursor] != "+":
                cursor -= 1
            if analysis[cursor] == "+":
                cursor += 1

            lemma = analysis[cursor:end]

            if group.startswith("+Num"):  # special case
                group = group[4:]
            inflection_category = SimpleLexicalCategory(group.replace("+", "").upper())

            return FSTLemma(lemma), inflection_category

        else:
            return None
    else:
        return None


def extract_simple_lc(analysis: str) -> Optional[SimpleLexicalCategory]:
    """
    :param analysis: in the form of 'a+VAI+b+c'
    :return: None if extraction fails
    """
    res = re.search(analysis_pattern, analysis)
    if res is not None:
        group = res.group("category")

        if group:
            if group.startswith("+Num"):  # special case
                group = group[4:]
            return SimpleLexicalCategory(group.replace("+", "").upper())
        else:
            return None
    else:
        return None
