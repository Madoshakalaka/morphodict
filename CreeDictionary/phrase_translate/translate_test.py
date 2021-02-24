import pytest

from phrase_translate.translate import inflect_english_phrase


@pytest.mark.parametrize(
    ("analysis", "definition", "english_phrase"),
    (
        ("masinahikan+N+Dim+Px1Sg+Loc", "book", "in my little book"),
        ("atâhk+N+A+Der/Dim+N+A+Obv", "star", "little star over there"),
        (
            "nêhiyawasinahikan+N+I+Der/Dim+N+I+Px1Sg+Loc",
            "Cree book",
            "in my little Cree book",
        ),
        # (
        #     "PV/e+wîtatoskêmêw+V+TA+Cnj+1Sg+2SgO",
        #     "s/he works together with s.o.",
        #     "I work together with you",
        # ),
        # (
        #     "PV/e+wîtapimêw+V+TA+Cnj+1Sg+2SgO",
        #     "s/he sits with s.o., s/he stays with s.o., s/he is present with s.o.",
        #     "I sit with you, I stay with you, I am present with you",
        # ),
    ),
)
def test_translations(analysis, definition, english_phrase):
    assert inflect_english_phrase(analysis, definition) == english_phrase


# kimaskomisinâhk
# kimâyi-isîhcikêwinisinawa
