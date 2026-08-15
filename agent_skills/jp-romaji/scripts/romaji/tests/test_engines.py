from romaji.cutlet_engine import convert as cutlet_convert
from romaji.pykakasi_engine import convert as pykakasi_convert


def test_pykakasi_tokens_nonempty_for_koi_wa_sensou():
    result = pykakasi_convert("恋は戦争")
    assert result["tokens"]
    for tok in result["tokens"]:
        assert set(tok) == {"orig", "hira", "kana", "romaji"}
        assert tok["orig"]


def test_cutlet_line_fields_present():
    result = cutlet_convert("恋は戦争")
    assert isinstance(result["hira"], str) and result["hira"]
    assert isinstance(result["kana"], str) and result["kana"]
    assert isinstance(result["romaji"], str) and result["romaji"]
    assert isinstance(result["tokens"], list)
