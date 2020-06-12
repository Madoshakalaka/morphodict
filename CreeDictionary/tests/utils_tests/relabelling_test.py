#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from io import StringIO

import pytest

from utils.fst_analysis_parser import Relabelling

labels = Relabelling.from_tsv(
    StringIO(
        """
FST TAG\tLINGUISTIC (SHORT)\tLINGUISTIC (LONG)\tENGLISH\tNÊHIYAWÊWIN\tEMOJI
3Sg+4Sg/PlO\t\t\ts/he → him/her/them\twiya → wiya/wiyawâw (ana/aniki)\t-
TA\tTransitive Animate\t\tlike: wîcihêw, itêw\ttâpiskôc: wîcihêw, itêw\t🧑🏽➡️🧑🏽
TI\tTransitive Inaminate\t\tlike: nâtam, mîciw\ttâpiskôc: nâtam, mîciw\t🧑🏽➡️📦
V\tVerb\t\tAction word\tispayin-itwêwin
V+AI\tAnimate intransitive verb\tVerb - animate intransitive\tAction word - like: mîcisow, nipâw\tispayin-itwêwin - tâpiskôc: mîcisow, nipâw
V+II\tInanimate intransitive verb\tVerb - inanimate intransitive\tAction word - like: miywâsin, mihkwâw\tispayin-itwêwin - tâpiskôc: miywâsin, mihkwâw
V+TA\tTransitive animate verb\tVerb - transitive animate\tAction word - like: wîcihêw, itêw\tispayin-itwêwin - tâpiskôc: wîcihêw, itêw
V+TI\tTransitive inanimate verb\tVerb - transitive inanimate\tAction word - like: nâtam, mîciw\tispayin-itwêwin - tâpiskôc: nâtam, mîciw
""".lstrip()
    )
)


def test_getting_a_pos_and_word_class_label():
    label = labels.linguistic_long.get_longest(("V", "TA"))
    assert label is not None
    assert "transitive" in label.lower()
    assert "animate" in label.lower()
    assert "verb" in label.lower()


def test_providing_an_entire_analysis_will_match_the_longest_prefix():
    label = labels.linguistic_long.get_longest(("V", "TA"))
    new_label = labels.linguistic_long.get_longest(
        ("V", "TA", "Prs", "Ind", "3Sg", "4Sg/PlO")
    )
    assert new_label == label


def test_getting_a_label_that_does_not_exist_returns_none():
    label = labels.linguistic_short.get_longest(("Not", "Real", "Labels"))
    assert label is None


def test_it_still_works_like_get_if_given_just_one_tag():
    label = labels.linguistic_short.get_longest(("V",))
    assert "verb" == label.lower()


@pytest.mark.parametrize("key", ["V", ("V",), ("V", "TA")])
def test_contains_tag_sets(key):
    assert key in labels
