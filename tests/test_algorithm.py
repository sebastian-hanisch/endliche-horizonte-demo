"""Mini-Instanz-Tests je Einheit (DEMO-PLAYBOOK §1b): alles von Hand gerechnet, Auszahlungen 5/3/1/0."""

import pytest

import ehz_algorithm as A
import ehz_constants as C
from ehz_scenario import stage_payoff, tft_dk_action, tft_dk_label

CC, DD = C.COOPERATE, C.DEFECT


def test_stage_payoffs():
    assert stage_payoff(0, 0) == 3 and stage_payoff(0, 1) == 0 and stage_payoff(1, 0) == 5 and stage_payoff(1, 1) == 1


def test_tft_dk_action():
    assert [tft_dk_action(t, CC, 5, 0) for t in range(1, 6)] == [CC] * 5                 # gewöhnliches Tit-for-Tat gegen Kooperation
    assert [tft_dk_action(t, CC, 5, 2) for t in range(1, 6)] == [CC, CC, CC, DD, DD]
    assert tft_dk_action(2, DD, 5, 0) == DD                                              # spiegelt die Defektion
    assert [tft_dk_action(t, CC, 3, 3) for t in range(1, 4)] == [DD] * 3                 # k = N: Immer-Defektieren
    with pytest.raises(ValueError):
        tft_dk_action(1, CC, 3, 4)
    with pytest.raises(ValueError):
        tft_dk_action(4, CC, 3, 0)


def test_labels():
    assert tft_dk_label(0, 10) == "Tit-for-Tat"
    assert tft_dk_label(1, 10) == "Tit-for-Tat, defektiert in der letzten Runde"
    assert tft_dk_label(3, 10) == "Tit-for-Tat, defektiert in den letzten 3 Runden"
    assert tft_dk_label(10, 10) == "Immer defektieren"


def test_best_response_to_tft_by_hand():
    # N = 1: nur eine Runde: D bringt 5. N = 2: C, D = 3 + 5 = 8 (D, D = 5 + 1 = 6; C, C = 6). N = 3: C, C, D = 3 + 3 + 5 = 11.
    assert A.best_response(1, 0) == (5.0, [DD])
    assert A.best_response(2, 0) == (8.0, [CC, DD])
    assert A.best_response(3, 0) == (11.0, [CC, CC, DD])


def test_best_response_is_always_two_more_than_cooperation():
    for n in (1, 2, 5, 10, 25):
        value, path = A.best_response(n, 0)
        assert value == pytest.approx(3 * n + 2) and A.first_defection(path) == n


def test_best_response_to_always_defect_is_always_defect():
    for n in (1, 3, 8):
        assert A.best_response(n, n) == (float(n), [DD] * n)


def test_best_response_chain_moves_one_round_earlier():
    chain = A.best_response_chain(8)
    firsts = [row["first_defection"] for row in chain]
    assert firsts[:8] == [8, 7, 6, 5, 4, 3, 2, 1]                                       # eine Runde früher je Schritt
    assert firsts[8] == 1                                                              # gegen Immer-Defektieren sofort
    assert [row["value"] for row in chain][:3] == [26.0, 24.0, 22.0]


def test_cooperation_value():
    assert A.cooperation_value(7) == 21.0


def test_random_horizon_with_zero_width_equals_the_fixed_horizon():
    r = A.random_horizon_best_response(10, 0)
    assert r["value"] == pytest.approx(32.0) and r["gain"] == pytest.approx(2.0) and r["first_defection"] == 10


def test_random_horizon_gain_is_two_over_w_plus_one():
    for w in (1, 2, 5, 10, 20):
        r = A.random_horizon_best_response(20, w)
        assert r["gain"] == pytest.approx(2.0 / (w + 1), abs=1e-9), w
        assert r["first_defection"] == 20 + w                                          # erst in der spätestmöglichen Runde
        assert r["expected_length"] == 20 + w / 2


def test_random_horizon_validates():
    with pytest.raises(ValueError):
        A.random_horizon_best_response(0, 3)
    with pytest.raises(ValueError):
        A.random_horizon_best_response(5, -1)


def test_geometric_gain_is_zero_from_two_thirds():
    assert A.geometric_gain(0.5) > 0.5
    assert A.geometric_gain(0.66) > 0.0
    assert A.geometric_gain(2 / 3 + 1e-6) == pytest.approx(0.0, abs=1e-6)
    assert A.geometric_gain(0.9) == 0.0
    with pytest.raises(ValueError):
        A.geometric_gain(1.0)


def test_backward_induction_table():
    rows = A.backward_induction_table(4)
    assert [r["rounds_left"] for r in rows] == [4, 3, 2, 1]
    assert [r["value_per_player"] for r in rows] == [4.0, 3.0, 2.0, 1.0]
    assert all(r["equilibrium_action"] == "defektieren" for r in rows)
