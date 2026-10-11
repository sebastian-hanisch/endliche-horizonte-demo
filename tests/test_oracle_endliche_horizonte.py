"""Orakel-Tests endliche-horizonte-demo: der Kern wird gegen UNABHÄNGIGE Rechenwege geprüft (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2).

1. Beste Antwort: Aufzählung aller 2^N Aktionsfolgen gegen TFT-Dk (N ≤ 12), gegen die Rückwärtsrechnung des Kerns.
2. Gleichgewichte des Zwei-Runden-Spiels: Aufzählung ALLER reinen Strategien beider Spieler (32 × 32) und aller Nash-Gleichgewichte; auf dem Pfad defektieren beide in
   beiden Runden.
3. Zufälliges Ende: Aufzählung aller Aktionsfolgen mit dem Erwartungswert über die Länge, gegen die Gefahrenraten-Rechnung.
4. Unbeschränktes Ende: der Vorteil in geschlossener Form aus den drei Kandidaten (Immer-D, Abwechseln, Kooperieren)."""

import itertools

import numpy as np
import pytest

import ehz_algorithm as A
import ehz_constants as C

U = {(0, 0): (3.0, 3.0), (0, 1): (0.0, 5.0), (1, 0): (5.0, 0.0), (1, 1): (1.0, 1.0)}


def tft_dk(n, k):
    """Aktionsfolge-Funktion des Gegners: Aktion in Runde t aus meiner Vorrunden-Aktion."""
    def act(t, my_prev):
        return 1 if t > n - k else my_prev
    return act


def sequence_value(seq, opp_act, n):
    total, prev = 0.0, 0
    for t in range(1, n + 1):
        b = opp_act(t, prev)
        a = seq[t - 1]
        total += U[(a, b)][0]
        prev = a
    return total


@pytest.mark.parametrize("n", [1, 2, 4, 7, 10, 12])
def test_best_response_matches_full_enumeration(n):
    for k in sorted({0, 1, max(0, n - 2), n}):
        opp = tft_dk(n, k)
        best = max(sequence_value(seq, opp, n) for seq in itertools.product((0, 1), repeat=n))
        assert A.best_response(n, k)[0] == pytest.approx(best), (n, k)


def test_two_round_game_has_a_unique_equilibrium_payoff_by_enumeration():
    """Reine Strategien im Zwei-Runden-Spiel: erste Aktion plus je eine Antwort auf jedes der vier Ergebnisse der ersten Runde."""
    outcomes = list(U)                                            # (meine Aktion, Aktion des anderen)
    strategies = [(first, dict(zip(outcomes, resp))) for first in (0, 1) for resp in itertools.product((0, 1), repeat=4)]
    assert len(strategies) == 32

    def play(s1, s2):
        a1, b1 = s1[0], s2[0]
        a2 = s1[1][(a1, b1)]
        b2 = s2[1][(b1, a1)]
        return U[(a1, b1)][0] + U[(a2, b2)][0], U[(a1, b1)][1] + U[(a2, b2)][1], (a1, a2, b1, b2)

    payoff = {(i, j): play(strategies[i], strategies[j]) for i in range(32) for j in range(32)}
    nash = []
    for i in range(32):
        for j in range(32):
            p1, p2, _ = payoff[(i, j)]
            if all(payoff[(x, j)][0] <= p1 + 1e-9 for x in range(32)) and all(payoff[(i, y)][1] <= p2 + 1e-9 for y in range(32)):
                nash.append((i, j))
    assert nash                                                   # es gibt Gleichgewichte
    assert {payoff[ij][:2] for ij in nash} == {(2.0, 2.0)}        # alle haben die Auszahlungen (2 / 2) = N · P
    assert {payoff[ij][2] for ij in nash} == {(1, 1, 1, 1)}       # und defektieren auf dem Pfad in beiden Runden


@pytest.mark.parametrize("n_min,w", [(3, 0), (3, 2), (5, 4), (4, 8)])
def test_random_horizon_matches_full_enumeration(n_min, w):
    t_max = n_min + w
    lengths = list(range(n_min, t_max + 1))
    best = -1.0
    for seq in itertools.product((0, 1), repeat=t_max):
        expected = 0.0
        for length in lengths:
            total, prev = 0.0, 0
            for t in range(1, length + 1):
                a = seq[t - 1]
                total += U[(a, prev)][0]                          # Tit-for-Tat spielt meine Vorrunden-Aktion
                prev = a
            expected += total / len(lengths)
        best = max(best, expected)
    assert A.random_horizon_best_response(n_min, w)["value"] == pytest.approx(best, abs=1e-9)


@pytest.mark.parametrize("delta", [0.2, 0.4, 0.5, 0.6, 0.66, 0.67, 0.8, 0.95])
def test_geometric_gain_matches_the_closed_form_of_the_three_candidates(delta):
    t, r, p, s = C.T, C.R, C.P, C.S
    cooperate = r / (1 - delta)
    always_defect = t + delta * p / (1 - delta)
    alternate = (t + delta * s) / (1 - delta ** 2)
    expected = max(0.0, always_defect - cooperate, alternate - cooperate)
    assert A.geometric_gain(delta) == pytest.approx(expected, abs=1e-8), delta


def test_the_unbounded_threshold_is_two_thirds():
    below = A.geometric_gain(2 / 3 - 0.01)
    above = A.geometric_gain(2 / 3 + 0.01)
    assert below > 1e-4 and above == pytest.approx(0.0, abs=1e-9)
    # numerisch: für δ < 2/3 ist Abwechseln der bessere Kandidat
    d = 0.6
    assert (C.T + d * C.S) / (1 - d ** 2) > C.T + d * C.P / (1 - d)
    assert np.isfinite(A.geometric_gain(d))
