import time

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse


@pytest.fixture(scope="module")
def django_db_setup():
    """
    This works with pytest-django plugin.
    This fixture tells all functions marked with pytest.mark.django_db in this file
    to use the database specified in settings.py
    which is the existing test_db.sqlite3 if USE_TEST_DB=True is passed.

    Instead of by default, an empty database in memory.
    """

    # all functions in this file should use the existing test_db.sqlite3
    assert settings.USE_TEST_DB


@pytest.mark.django_db
def test_click_in_text_correct_usage(client):
    # niskak means goose in plains Cree
    response = client.get(
        reverse("cree-dictionary-word-click-in-text-api") + "?q=niskak"
    )

    assert b"goose" in response.content


@pytest.mark.django_db
def test_click_in_text_no_params(client):
    response = client.get(reverse("cree-dictionary-word-click-in-text-api"))

    assert response.status_code == 400


ASCII_WAPAMEW = "wapamew"
EXPECTED_SUFFIX_SEARCH_RESULT = "asawâpamêw"


@pytest.mark.django_db
def test_normal_search_uses_affix_search(client):
    """
    Regular dictionary search should return affix results.

    e.g.,

    > search?q=wapamew
    should return both "wâpamêw" and "asawâpamêw"
    """
    normal_search_response = client.get(
        reverse("cree-dictionary-search") + f"?q={ASCII_WAPAMEW}"
    ).content.decode("utf-8")
    assert EXPECTED_SUFFIX_SEARCH_RESULT in normal_search_response


@pytest.mark.django_db
def test_click_in_text_disables_affix_search(client):
    """
    The Click-in-Text API should NOT return affix results — too many results!

    e.g.,

    > search?q=wapamew
    should return "wâpamêw" but NOT "asawâpamêw"
    """
    click_in_text_response = client.get(
        reverse("cree-dictionary-word-click-in-text-api") + f"?q={ASCII_WAPAMEW}"
    ).content.decode("utf-8")
    assert EXPECTED_SUFFIX_SEARCH_RESULT not in click_in_text_response
