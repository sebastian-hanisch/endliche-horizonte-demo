"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

COOPERATE, DEFECT = 0, 1

# Auszahlungen je Runde (Axelrod), fest.
T, R, P, S = 5.0, 3.0, 1.0, 0.0

N_MIN, N_MAX, DEFAULT_N, N_STEP = 3, 40, 10, 1
K_MIN = 0
W_MIN, W_MAX, DEFAULT_W, W_STEP = 0, 40, 5, 1
DEFAULT_START = 20                    # früheste Länge im Experiment „unsicheres Ende“

N_CURVE = (1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 40, 60, 80, 100)
W_CURVE = (0, 1, 2, 3, 5, 8, 10, 15, 20, 30, 40)
DELTA_CURVE = tuple(round(0.05 * i, 2) for i in range(2, 20))     # 0,10 bis 0,95

TOL = 1e-9

COLOR_BR = "#2F6B65"
COLOR_TFT = "#4c78a8"
COLOR_ALLD = "#B5483A"
COLOR_UNBOUNDED = "#e08a2c"
COLOR_OTHER = "rgba(150,150,150,0.55)"

PRESETS = {
    "Rahmenvertrag über 10 Wochen": {"n": 10, "w": 5},
    "Sehr kurzer Vertrag (3 Wochen)": {"n": 3, "w": 5},
    "Langer Vertrag (40 Wochen)": {"n": 40, "w": 5},
    "Enddatum unsicher (20 bis 25 Wochen)": {"n": 20, "w": 5},
    "Enddatum sehr unsicher (20 bis 60 Wochen)": {"n": 20, "w": 40},
}
PRESET_HELP = {
    "Rahmenvertrag über 10 Wochen": "Bekanntes Ende nach Woche 10: gegen Tit-for-Tat lohnt es sich, in der letzten Woche zu defektieren.",
    "Sehr kurzer Vertrag (3 Wochen)": "Auch bei drei Wochen gibt es noch einen Vorteil durch das Defektieren in der letzten Woche: genau 2 Punkte.",
    "Langer Vertrag (40 Wochen)": "Der Vorteil bleibt absolut 2 Punkte, je Woche aber nur 0,05: gut für ein Tit-for-Tat-Paar, kein Gleichgewicht im strengen Sinn.",
    "Enddatum unsicher (20 bis 25 Wochen)": "Das Ende liegt gleichverteilt zwischen Woche 20 und 25: der Vorteil schrumpft auf ein Sechstel von 2.",
    "Enddatum sehr unsicher (20 bis 60 Wochen)": "Je weiter das mögliche Ende auseinanderliegt, desto kleiner der Anreiz, in der spätestmöglichen Woche zu defektieren.",
}
