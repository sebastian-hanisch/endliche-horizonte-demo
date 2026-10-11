"""Kennzahlen, Verdikt-Logik und Auswertungen über den Kern (die Komposition der Einheiten aus ehz_algorithm)."""

from dataclasses import dataclass

import ehz_algorithm as A
import ehz_constants as C
from ehz_scenario import stage_payoff, tft_dk_action, tft_dk_label


def fmt(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def action_string(actions) -> str:
    return " ".join("C" if a == C.COOPERATE else "D" for a in actions)


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    w: int = C.DEFAULT_W


@dataclass(frozen=True)
class Analysis:
    n: int
    br_value: float
    coop_value: float
    gain: float
    first_defection: int | None
    path: tuple[int, ...]
    chain: tuple[dict, ...]
    random: dict                          # Ergebnis der Rechnung mit zufälligem Ende (n bis n + w)
    expected_delta: float                 # Fortsetzungswahrscheinlichkeit mit derselben erwarteten Dauer wie n
    geometric_gain_per_round: float       # Vorteil je erwarteter Runde bei unbeschränktem Ende gleicher Erwartung


def analyse(settings: Settings) -> Analysis:
    n = settings.n
    br_value, path = A.best_response(n, 0)
    delta = 1.0 - 1.0 / n if n >= 2 else 0.5
    geo = A.geometric_gain(delta) * (1.0 - delta) if delta > 0.0 else 0.0
    return Analysis(
        n=n, br_value=br_value, coop_value=A.cooperation_value(n), gain=br_value - A.cooperation_value(n),
        first_defection=A.first_defection(path), path=tuple(path), chain=tuple(A.best_response_chain(n)),
        random=A.random_horizon_best_response(n, settings.w), expected_delta=delta, geometric_gain_per_round=geo,
    )


def strategy_overview(n: int) -> list[dict]:
    """Je k: Beschreibung und die Aktionen der Strategie TFT-Dk gegen Tit-for-Tat über n Runden (beide spielen die Strategie des Namens)."""
    rows = []
    for k in sorted({0, 1, 2, max(0, n - 1), n}):
        mine, theirs, prev_me, prev_opp = [], [], C.COOPERATE, C.COOPERATE
        for t in range(1, n + 1):
            a = tft_dk_action(t, prev_opp, n, k)
            b = tft_dk_action(t, prev_me, n, 0)
            mine.append(a)
            theirs.append(b)
            prev_me, prev_opp = a, b
        pay = sum(stage_payoff(a, b) for a, b in zip(mine, theirs))
        rows.append({"k": k, "label": tft_dk_label(k, n), "mine": action_string(mine), "theirs": action_string(theirs), "payoff": pay})
    return rows


def gain_curves(n_values=C.N_CURVE) -> dict:
    """Vorteil der besten Antwort gegen Tit-for-Tat bei bekanntem Ende der Länge N (absolut und je Runde) gegen unbeschränktes Ende mit gleicher Erwartung."""
    absolute, per_round, geometric = [], [], []
    for n in n_values:
        value, _ = A.best_response(n, 0)
        absolute.append(value - A.cooperation_value(n))
        per_round.append((value - A.cooperation_value(n)) / n)
        if n >= 2:
            delta = 1.0 - 1.0 / n
            geometric.append(A.geometric_gain(delta) * (1.0 - delta))
        else:
            geometric.append(float("nan"))
    return {"n": list(n_values), "absolute": absolute, "per_round": per_round, "geometric_per_round": geometric}


def window_curves(n_min: int, widths=C.W_CURVE) -> dict:
    gains, first = [], []
    for w in widths:
        r = A.random_horizon_best_response(n_min, w)
        gains.append(r["gain"])
        first.append(r["first_defection"])
    return {"w": list(widths), "gain": gains, "first_defection": first, "closed_form": [2.0 / (w + 1) for w in widths]}


def verdict(an: Analysis, settings: Settings) -> tuple[str, str]:
    """(Stufe, Satz) für die Kernfrage: ist Tit-for-Tat gegen Tit-for-Tat bei bekanntem Ende ein Gleichgewicht?"""
    n = an.n
    if an.gain <= C.TOL:
        return "success", f"Bei {n} Runden lohnt Abweichen nicht."
    where = f"in Runde {an.first_defection}" if an.first_defection else "nie"
    return "warning", (f"Bei bekanntem Ende nach {n} Runden ist Tit-for-Tat gegen Tit-for-Tat **kein Gleichgewicht**: wer erst {where} (der letzten Runde) defektiert, "
                       f"bekommt {fmt(an.br_value, 0)} statt {fmt(an.coop_value, 0)}, also **{fmt(an.gain, 0)} Punkte mehr**, und der andere kann nicht mehr vergelten. "
                       f"Bei unbeschränktem Ende mit derselben erwarteten Dauer ({n} Runden, δ = {fmt(an.expected_delta)}) "
                       + ("ist es dagegen ein Gleichgewicht." if an.geometric_gain_per_round <= C.TOL else "lohnt Abweichen ebenfalls."))
