"""Kern der Demo (numpy/Standardbibliothek): das endlich oft wiederholte Gefangenendilemma, Rückwärtsinduktion und Beste Antworten.

Einheiten (DEMO-PLAYBOOK §1b):

- `best_response`          beste Antwort (Wert, Pfad) gegen einen reaktiven Gegner über n Runden, exakt per Rückwärtsrechnung
- `best_response_chain`    die Folge: beste Antwort auf TFT-Dk ist TFT-D(k+1) (eine Runde früher defektieren), bis Immer-Defektieren
- `cooperation_value`      Wert, wenn beide dauerhaft kooperieren
- `random_horizon_best_response`  dieselbe Rechnung bei zufälligem Ende (gleichverteilt über {n_min, …, n_min + w})
- `geometric_gain`         Vorteil der besten Antwort gegen Tit-for-Tat bei unbeschränktem Ende (Fortsetzungswahrscheinlichkeit δ)"""

import numpy as np

import ehz_constants as C
from ehz_scenario import stage_payoff, tft_dk_action


def best_response(n: int, k: int = 0) -> tuple[float, list[int]]:
    """Beste Antwort gegen TFT-Dk in einem Spiel über n Runden: (Gesamtwert, Aktionsfolge). Zustand der Rückwärtsrechnung: meine Vorrunden-Aktion."""
    if n < 1:
        raise ValueError("mindestens eine Runde")
    value = [[0.0, 0.0] for _ in range(n + 2)]
    policy = [[0, 0] for _ in range(n + 2)]
    for t in range(n, 0, -1):
        for prev in (C.COOPERATE, C.DEFECT):
            best, best_a = -1e18, C.COOPERATE
            for a in (C.COOPERATE, C.DEFECT):
                opp = tft_dk_action(t, prev, n, k)
                v = stage_payoff(a, opp) + value[t + 1][a]
                if v > best + C.TOL:                   # bei Gleichstand bleibt die Kooperation (die erste Wahl)
                    best, best_a = v, a
            value[t][prev], policy[t][prev] = best, best_a
    prev, path = C.COOPERATE, []
    for t in range(1, n + 1):
        a = policy[t][prev]
        path.append(a)
        prev = a
    return value[1][C.COOPERATE], path


def cooperation_value(n: int) -> float:
    """Gesamtwert, wenn beide in jeder der n Runden kooperieren: n · R."""
    return n * C.R


def first_defection(path: list[int]) -> int | None:
    """Runde (1-basiert) der ersten Defektion; None, wenn nie."""
    return path.index(C.DEFECT) + 1 if C.DEFECT in path else None


def best_response_chain(n: int) -> list[dict]:
    """Für k = 0 … n: die beste Antwort auf TFT-Dk, ihr Wert und ihre erste Defektion. Beobachtung: sie beginnt eine Runde früher als der Gegner."""
    rows = []
    for k in range(0, n + 1):
        value, path = best_response(n, k)
        rows.append({"k": k, "value": value, "first_defection": first_defection(path), "path": path})
    return rows


def random_horizon_best_response(n_min: int, w: int) -> dict:
    """Beste Antwort gegen Tit-for-Tat, wenn die Länge T gleichverteilt über {n_min, …, n_min + w} ist.

    Nach Runde t endet das Spiel mit der Gefahrenrate h_t = P(T = t | T ≥ t); Wert V_t(prev) = max_a [u(a, prev) + (1 − h_t) V_{t+1}(a)]."""
    if n_min < 1 or w < 0:
        raise ValueError("n_min ≥ 1 und w ≥ 0")
    t_max = n_min + w
    pmf = np.zeros(t_max + 2)
    pmf[n_min: t_max + 1] = 1.0 / (w + 1)
    survive = np.cumsum(pmf[::-1])[::-1]                    # P(T ≥ t)
    value = np.zeros((t_max + 2, 2))
    policy = np.zeros((t_max + 2, 2), dtype=int)
    for t in range(t_max, 0, -1):
        hazard = pmf[t] / survive[t] if survive[t] > 0 else 1.0
        for prev in (C.COOPERATE, C.DEFECT):
            best, best_a = -1e18, C.COOPERATE
            for a in (C.COOPERATE, C.DEFECT):
                v = stage_payoff(a, prev) + (1.0 - hazard) * value[t + 1][a]
                if v > best + C.TOL:
                    best, best_a = v, a
            value[t][prev], policy[t][prev] = best, best_a
    prev, path = C.COOPERATE, []
    for t in range(1, t_max + 1):
        a = int(policy[t][prev])
        path.append(a)
        prev = a
    expected = n_min + w / 2.0
    return {"value": float(value[1][C.COOPERATE]), "path": path, "t_max": t_max, "expected_length": expected,
            "cooperation_value": C.R * expected, "gain": float(value[1][C.COOPERATE]) - C.R * expected,
            "first_defection": first_defection(path)}


def geometric_gain(delta: float) -> float:
    """Gewinn der besten Antwort gegen Tit-for-Tat bei unbeschränktem Ende (nach jeder Runde weiter mit Wahrscheinlichkeit δ), in diskontierten
    Einheiten: V_BR − R/(1 − δ). Null ab δ = 2/3 (Tit-for-Tat gegen Tit-for-Tat ist dann ein Gleichgewicht)."""
    if not 0.0 < delta < 1.0:
        raise ValueError("δ muss in (0, 1) liegen")
    v = np.zeros(2)                                          # Wert je meiner Vorrunden-Aktion
    for _ in range(100000):
        new = np.array([max(stage_payoff(a, prev) + delta * v[a] for a in (0, 1)) for prev in (0, 1)])
        if np.max(np.abs(new - v)) < 1e-12:
            v = new
            break
        v = new
    return max(0.0, float(v[C.COOPERATE] - C.R / (1.0 - delta)))     # numerisches −0 abfangen; der Vorteil ist nie negativ (Kooperieren ist erlaubt)


def backward_induction_table(n: int) -> list[dict]:
    """Rückwärtsinduktion im Spiel über n Runden: In Runde n ist Defektion strikt besser (5 > 3 und 1 > 0), egal was vorher geschah. Damit ist die
    Fortsetzung in Runde n − 1 festgelegt (beide defektieren), also ist dort Defektion strikt besser, und so weiter. Je Runde: die Zahl der
    Folgerunden und der gemeinsame Wert der Teilspiele unter dem Gleichgewicht (P je Runde)."""
    return [{"round": t, "rounds_left": n - t + 1, "equilibrium_action": "defektieren", "value_per_player": (n - t + 1) * C.P}
            for t in range(1, n + 1)]
