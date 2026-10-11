"""Jede Zahl aus README und App wird hier über die echten Auswertungsfunktionen nachgerechnet (DEMO-PLAYBOOK §4)."""

import pytest

import ehz_algorithm as A
import ehz_constants as C
import ehz_evaluation as E


def test_the_gain_of_the_best_response_is_exactly_two_for_every_length():
    for n in (1, 2, 3, 5, 10, 20, 40, 100):
        value, path = A.best_response(n, 0)
        assert value - 3 * n == pytest.approx(2.0), n
        assert A.first_defection(path) == n


def test_gain_per_round_curve():
    curves = E.gain_curves((2, 5, 10, 40))
    assert curves["per_round"] == pytest.approx([1.0, 0.4, 0.2, 0.05])
    assert curves["absolute"] == pytest.approx([2.0] * 4)


def test_unbounded_end_with_the_same_expected_length():
    curves = E.gain_curves((2, 3, 5, 10))
    assert curves["geometric_per_round"][0] == pytest.approx(0.333, abs=0.001)     # N = 2: δ = 1/2
    assert curves["geometric_per_round"][1] == pytest.approx(0.0, abs=1e-6)        # N = 3: δ = 2/3, Schwelle
    assert curves["geometric_per_round"][2:] == pytest.approx([0.0, 0.0], abs=1e-9)


def test_best_response_chain_at_n_10():
    chain = A.best_response_chain(10)
    assert [r["first_defection"] for r in chain] == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 1]
    assert [r["value"] for r in chain] == [32.0, 30.0, 28.0, 26.0, 24.0, 22.0, 20.0, 18.0, 16.0, 14.0, 10.0]


def test_equilibrium_value_at_n_10():
    an = E.analyse(E.Settings(n=10, w=5))
    assert an.coop_value == 30.0 and an.br_value == 32.0 and an.gain == 2.0
    assert 10 * C.P == 10.0 and 10 * (C.R - C.P) == 20.0           # der Preis des bekannten Endes: 30 statt 10


def test_random_horizon_numbers():
    expected = {0: 2.0, 1: 1.0, 2: 2 / 3, 5: 1 / 3, 10: 2 / 11, 20: 2 / 21, 40: 2 / 41}
    for w, gain in expected.items():
        r = A.random_horizon_best_response(20, w)
        assert r["gain"] == pytest.approx(gain, abs=1e-9)
        assert r["first_defection"] == 20 + w
    r = A.random_horizon_best_response(20, 5)
    assert r["expected_length"] == 22.5 and r["cooperation_value"] == pytest.approx(67.5) and r["value"] == pytest.approx(67.5 + 1 / 3)


def test_strategy_overview_traces_by_hand():
    rows = {r["k"]: r for r in E.strategy_overview(10)}
    assert rows[0]["mine"] == "C C C C C C C C C C" and rows[0]["payoff"] == 30.0
    assert rows[1]["mine"] == "C C C C C C C C C D" and rows[1]["theirs"] == "C C C C C C C C C C" and rows[1]["payoff"] == 32.0
    assert rows[2]["mine"] == "C C C C C C C C D D" and rows[2]["theirs"] == "C C C C C C C C C D" and rows[2]["payoff"] == 30.0
    assert rows[10]["mine"] == "D D D D D D D D D D" and rows[10]["payoff"] == 14.0
    assert rows[9]["payoff"] == 16.0


def test_verdict_texts():
    an = E.analyse(E.Settings(n=10, w=5))
    level, text = E.verdict(an, E.Settings(n=10, w=5))
    assert level == "warning" and "kein Gleichgewicht" in text and "2 Punkte mehr" in text and "ist es dagegen ein Gleichgewicht" in text
    short = E.analyse(E.Settings(n=3, w=0))
    assert "ist es dagegen ein Gleichgewicht" in E.verdict(short, E.Settings(n=3, w=0))[1]       # δ = 2/3: gerade noch
    one_round_less = E.analyse(E.Settings(n=3, w=0))
    assert one_round_less.geometric_gain_per_round == pytest.approx(0.0, abs=1e-6)


def test_preset_stories():
    for name, p in C.PRESETS.items():
        an = E.analyse(E.Settings(p["n"], p["w"]))
        assert an.gain == pytest.approx(2.0), name
    assert A.random_horizon_best_response(20, 5)["gain"] == pytest.approx(1 / 3)       # „ein Sechstel von 2“
