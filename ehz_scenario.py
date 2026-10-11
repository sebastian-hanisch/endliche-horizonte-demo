"""Szenario: das Gefangenendilemma 5/3/1/0 über eine feste oder zufällige Zahl von Runden, und die Strategie „Tit-for-Tat, am Ende defektierend“.

`TFT-Dk` spielt Tit-for-Tat, defektiert aber in den letzten k Runden unabhängig vom Gegner. `TFT-D0` ist gewöhnliches Tit-for-Tat; mit k = N ist es
Immer-Defektieren. Der Gegner hängt von der Aktion des Spielers in der Vorrunde ab (reaktiv) und von der Rundennummer."""

import ehz_constants as C


def stage_payoff(own: int, other: int) -> float:
    """Auszahlung einer Runde für die eigene Aktion gegen die des anderen (0 = C, 1 = D)."""
    if own == C.COOPERATE:
        return C.R if other == C.COOPERATE else C.S
    return C.T if other == C.COOPERATE else C.P


def tft_dk_action(t: int, prev_of_other: int, n: int, k: int) -> int:
    """Aktion von TFT-Dk in Runde t (1-basiert) bei einem Spiel über n Runden, wenn der andere zuletzt `prev_of_other` gespielt hat
    (in Runde 1 gilt 0 = kooperiert): in den letzten k Runden defektieren, sonst die letzte Aktion des anderen."""
    if k < 0 or k > n:
        raise ValueError("k muss zwischen 0 und n liegen")
    if t < 1 or t > n:
        raise ValueError("Runde außerhalb des Spiels")
    return C.DEFECT if t > n - k else prev_of_other


def tft_dk_label(k: int, n: int) -> str:
    if k == 0:
        return "Tit-for-Tat"
    if k >= n:
        return "Immer defektieren"
    if k == 1:
        return "Tit-for-Tat, defektiert in der letzten Runde"
    return f"Tit-for-Tat, defektiert in den letzten {k} Runden"
