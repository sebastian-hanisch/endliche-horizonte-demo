"""Endliche Horizonte: Rückwärtsinduktion - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Sechstes Stück der Wiederholte-Spiele-Linie: Was passiert mit der Kooperation, wenn das Ende der Beziehung bekannt ist? Rückwärtsinduktion, die Kette der besten
Antworten, der kleine Vorteil des letzten Zuges (ε-Gleichgewicht) und der Unterschied zwischen bekanntem, unsicherem und unbeschränktem Ende.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import ehz_algorithm as A
import ehz_constants as C
import ehz_evaluation as E
from ehz_evaluation import Settings, fmt
from ehz_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from ehz_visualization import build_chain, build_gain_curves, build_window

st.set_page_config(page_title="Endliche Horizonte: Rückwärtsinduktion – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _overview(n):
    return E.strategy_overview(n)


@st.cache_data(show_spinner=False)
def _gain_curves():
    return E.gain_curves()


@st.cache_data(show_spinner=False)
def _window(n):
    return E.window_curves(n)


st.title("⏳ Endliche Horizonte: Rückwärtsinduktion")
st.markdown(
    """
Zwei Spediteure haben einen **Rahmenvertrag über N Wochen** und beide wissen das. In jeder Woche kann jeder eine Rückladung anbieten (kooperieren) oder nur
nutzen (defektieren). Was bisher galt, gilt nicht mehr: **Wer weiß, dass es zu Ende ist, hat in der letzten Woche nichts mehr zu verlieren.** Die Vergeltung
fällt weg, also defektiert er dort, und wenn das beide wissen, gilt dasselbe für die vorletzte Woche, und so weiter bis zur ersten.

Diese Demo rechnet das **exakt** nach und zeigt drei Dinge, die sich daran ändern, wie man es erst vermutet: der Vorteil des letzten Zuges ist nur **2 Punkte** (egal wie
lang der Vertrag ist), er verschwindet nicht durch Unsicherheit über das Ende, aber er **schrumpft**, und es kommt nicht darauf an, ob das Ende *bekannt* ist, sondern
ob es ein **spätestes** Ende gibt.

Weiter unten: **❓ Kernfrage**, drei Experimente (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Vorgänger ist
[folk-theorem-demo](https://sebastianhanisch-folk-theorem-demo.streamlit.app/): dort ging es um unendlich oft wiederholte Spiele.
"""
)

with st.expander("So funktioniert Rückwärtsinduktion", expanded=True):
    st.markdown(
        """
1. **Letzte Runde:** Es gibt keine Zukunft mehr, die man verlieren könnte. Defektieren bringt immer mehr (5 statt 3, 1 statt 0). Beide defektieren.
2. **Vorletzte Runde:** Was in der letzten Runde passiert, steht fest (beide defektieren), egal was jetzt geschieht. Also ist Defektieren jetzt wieder strikt besser.
3. **So weiter bis Runde 1:** In jeder Runde ist die Fortsetzung schon festgelegt, also ist Defektieren immer die beste Wahl. Das einzige Gleichgewicht ist
   „immer defektieren“, auch wenn die Beziehung 100 Runden dauert.
        """
    )

with st.expander("Die Strategien: wer macht was?", expanded=True):
    st.markdown(
        "**Tit-for-Tat** spielt zuerst Kooperation und danach die letzte Aktion des anderen. **Tit-for-Tat, am Ende defektierend (TFT-Dk)** spielt wie Tit-for-Tat, "
        "defektiert aber in den letzten k Runden immer. **Immer defektieren** ist TFT-Dk mit k = N. Die Tabelle zeigt, was die Strategie des Namens spielt, wenn sie "
        "gegen gewöhnliches Tit-for-Tat antritt, und was sie dabei bekommt."
    )
    rows = ["| Strategie | Aktionen der Strategie | Aktionen von Tit-for-Tat | Gesamtwert |", "|---|---|---|---|"]
    for r in _overview(st.session_state.get("n_slider", C.DEFAULT_N)):
        rows.append(f"| **{r['label']}** | `{r['mine']}` | `{r['theirs']}` | {fmt(r['payoff'], 0)} |")
    st.markdown("\n".join(rows))
    st.caption("Beobachtung: nur in der letzten Runde zu defektieren bringt 2 Punkte; eine Runde früher damit anzufangen kostet die Vergeltung und ist gleich viel wert wie nichts zu tun.")

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
cols = st.columns(len(C.PRESETS))
for col, name in zip(cols, C.PRESETS):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Beziehung**")
    n = st.slider("Länge des Vertrags N (Runden)", *bounds("n_slider"), step=C.N_STEP, key="n_slider", help="Wie viele Wochen der Vertrag läuft, wenn das Ende bekannt ist.")
    w = st.slider("Spanne w bei unsicherem Ende", *bounds("w_slider"), step=C.W_STEP, key="w_slider",
                  help="Experiment 3: Das Ende liegt gleichverteilt zwischen Runde N und Runde N + w. Bei 0 ist es bekannt.")

sync_query_params({"n_slider": int(n), "w_slider": int(w)})

settings = Settings(int(n), int(w))
an = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown(f"## 🎬 Kette der besten Antworten bei N = {an.n} Runden")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Beide kooperieren", fmt(an.coop_value, 0), delta="N · 3", delta_color="off")
m2.metric("Beste Antwort auf Tit-for-Tat", fmt(an.br_value, 0), delta=f"+{fmt(an.gain, 0)} gegenüber Kooperieren", delta_color="off")
m3.metric("Erste Defektion der besten Antwort", f"Runde {an.first_defection}" if an.first_defection else "nie", delta="die letzte Runde", delta_color="off")
m4.metric("Vorteil je Runde", fmt(an.gain / an.n, 3), delta=f"{fmt(an.gain, 0)} / {an.n}", delta_color="off")
st.plotly_chart(build_chain(an.chain, an.n), width="stretch", key="chain_chart")
st.caption(
    "Wenn der Gegner in den letzten k Runden defektiert, ist die beste Antwort darauf, **eine Runde früher** zu defektieren (erste Defektion bei Runde N − k). "
    "Jede Antwort ruft die nächste hervor, bis es bei k = N − 1 in Runde 1 beginnt: das ist die Rückwärtsinduktion als Kette."
)

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Ist Tit-for-Tat bei bekanntem Ende ein Gleichgewicht?")
level, sentence = E.verdict(an, settings)
{"success": st.success, "warning": st.warning, "info": st.info}[level](sentence)
st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie groß ist der Vorteil des letzten Zuges?")
st.caption("Vorteil der besten Antwort gegen Tit-for-Tat, je Runde, bei bekanntem Ende nach N Runden (grün) und bei unbeschränktem Ende mit derselben erwarteten Dauer (orange).")
curves = _gain_curves()
st.plotly_chart(build_gain_curves(curves), width="stretch", key="gain_chart")
st.info(
    "Der Vorteil ist bei bekanntem Ende **immer genau 2 Punkte** (für jede Länge ab einer Runde), je Runde also 2/N. Das ist ein **ε-Gleichgewicht** mit ε = 2 insgesamt (Radner 1980): "
    "bei langem Vertrag fast kein Anreiz, aber streng genommen kein Gleichgewicht. Bei unbeschränktem Ende mit derselben erwarteten Dauer ist Tit-for-Tat ab "
    "3 Runden (δ = 2/3) ein **exaktes** Gleichgewicht: der Vorteil ist null."
)
st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wo beginnt die Rückwärtsinduktion bei zufälligem Ende?")
st.caption(f"Das Ende liegt gleichverteilt zwischen Runde {settings.n} und Runde {settings.n + settings.w} (Spanne w aus der Seitenleiste); die beste Antwort gegen Tit-for-Tat wird "
           "exakt über die Rückwärtsrechnung mit der Gefahrenrate je Runde bestimmt.")
r = an.random
c1, c2, c3 = st.columns(3)
c1.metric("Erwartete Länge", fmt(r["expected_length"], 1) + " Runden", delta=f"von {settings.n} bis {r['t_max']}", delta_color="off")
c2.metric("Vorteil der besten Antwort", fmt(r["gain"], 3), delta=f"= 2 / ({settings.w} + 1) = {fmt(2 / (settings.w + 1), 3)}", delta_color="off")
c3.metric("Erste Defektion", f"Runde {r['first_defection']}", delta="die spätestmögliche Runde", delta_color="off")
st.plotly_chart(build_window(_window(settings.n)), width="stretch", key="window_chart")
st.info(
    "Auch bei unsicherem Ende defektiert die beste Antwort gegen Tit-for-Tat erst in der **spätestmöglichen** Runde, und der Vorteil ist 2 mal der Wahrscheinlichkeit, "
    "dass das Spiel dort wirklich endet, also **2 / (w + 1)**. Unsicherheit macht den Anreiz kleiner, beseitigt ihn aber nicht, solange es ein spätestes Ende gibt."
)
st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Die Rückwärtsinduktion Runde für Runde")
st.caption(f"Im Gleichgewicht defektieren beide in jeder der {settings.n} Runden. Wert je Spieler im Teilspiel ab Runde t: (verbleibende Runden) · 1.")
table = ["| Runde | Verbleibende Runden | Gleichgewichtsaktion | Wert je Spieler im Teilspiel |", "|---|---|---|---|"]
for row in A.backward_induction_table(settings.n)[:12]:
    table.append(f"| {row['round']} | {row['rounds_left']} | {row['equilibrium_action']} | {fmt(row['value_per_player'], 0)} |")
if settings.n > 12:
    table.append(f"| … | … | … | … |")
st.markdown("\n".join(table))
st.info(f"Beide bekommen im Gleichgewicht {fmt(settings.n * C.P, 0)} Punkte statt {fmt(settings.n * C.R, 0)} bei dauerhafter Kooperation: der Preis des bekannten Endes sind "
        f"{fmt(settings.n * (C.R - C.P), 0)} Punkte je Spieler.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Das Ende ist allen bekannt, und alle wissen, dass alle es wissen** | Die Rückwärtsinduktion braucht gemeinsames Wissen über das Ende; bei Zweifeln an der Rationalität des anderen kann sich Kooperation lohnen (Kreps, Milgrom, Roberts, Wilson 1982), das ist hier nicht modelliert. | - |
| **Beide rechnen exakt rückwärts** | Die Rechnung sagt, was rational wäre; ob Menschen so spielen, ist eine empirische Frage, die diese Demo nicht beantwortet. | - |
| **Genau die Auszahlungen 5/3/1/0** | Die Größe des Vorteils (2) hängt an T − R; bei anderen Auszahlungen ändert sich der Betrag, nicht die Logik. | - |
| **Strikte Dominanz in der letzten Runde** | Gäbe es dort mehrere Gleichgewichte, ließe sich Kooperation früher mit Drohungen stützen (Benoit und Krishna 1985). Im Gefangenendilemma gibt es nur eins. | - |
| **Beste Antwort gegen eine reaktive Strategie** | Gegen Strategien mit längerem Gedächtnis gelten dieselben Aussagen, aber die Rechnung wäre größer. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Rückwärtsinduktion.** In Runde $N$ gilt $u(D, y) > u(C, y)$ für jedes $y$, also spielt jede Gleichgewichtsstrategie auf jedem erreichbaren Pfad $D$. Mit
dieser festen Fortsetzung gilt das in Runde $N-1$ ebenso, und so weiter. Einziges Nash- und teilspielperfektes Gleichgewicht: in jeder Runde $D$, Wert $N \cdot P$.

**Beste Antwort gegen Tit-for-Tat.** Zustand ist meine Vorrunden-Aktion $a_{t-1}$, die Aktion von Tit-for-Tat in $t$. Rückwärtsrechnung
$V_t(a_{t-1}) = \max_a \big[u(a, a_{t-1}) + V_{t+1}(a)\big]$, $V_{N+1} = 0$. Ergebnis: Kooperation bis Runde $N-1$ und Defektion in $N$, Wert $3N + 2$.

**ε-Gleichgewicht (Radner 1980).** Tit-for-Tat gegen Tit-for-Tat ist ein ε-Gleichgewicht mit $\varepsilon = T - R = 2$ insgesamt, also $2/N$ je Runde.

**Zufälliges Ende.** Ist $T$ gleichverteilt über $\{N, \dots, N+w\}$, endet das Spiel nach Runde $t$ mit der Gefahrenrate
$h_t = P(T = t \mid T \ge t)$ und $V_t(p) = \max_a \big[u(a,p) + (1 - h_t)\,V_{t+1}(a)\big]$. Die beste Antwort defektiert erst in $t_{\max} = N + w$ und gewinnt
$2 \cdot P(T = t_{\max}) = 2/(w+1)$.

**Unbeschränktes Ende.** Setzt das Spiel mit Wahrscheinlichkeit $\delta$ fort, ist Tit-for-Tat gegen Tit-for-Tat ein exaktes Gleichgewicht für
$\delta \ge \max\{\tfrac{T-R}{T-P}, \tfrac{T-R}{R-S}\} = \tfrac23$ (tit-for-tat-demo), die erwartete Länge ist $1/(1-\delta)$.

**Literatur.** Radner (1980), *Collusive behavior in noncooperative epsilon-equilibria of oligopolies with long but finite lives*, Journal of Economic Theory 22, 136–154 (ε-Gleichgewichte bei langem, aber endlichem Horizont); Kreps, Milgrom, Roberts und Wilson (1982), *Rational cooperation in the finitely repeated prisoners' dilemma*, Journal of Economic Theory 27, 245–252 (Kooperation durch unvollständige Information); Benoit und Krishna (1985), *Finitely repeated games*, Econometrica 53, 905–922 (Folk-Theorem für endliche Wiederholung, wenn das Stufenspiel mehrere Gleichgewichte hat). Nur Zusammenfassungen gelesen. Der Vorteil von genau 2 Punkten und 2/(w + 1) bei zufälligem Ende sind hier gerechnet und per Aufzählung geprüft, nicht aus der Literatur übernommen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
