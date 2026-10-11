# Endliche Horizonte: Rückwärtsinduktion – Streamlit-Demo

<!-- Nach dem Deploy direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-endliche-horizonte-demo.streamlit.app/)** -->

Sechstes Stück der **Wiederholte-Spiele-Linie** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Kontrast zu [folk-theorem-demo](https://sebastianhanisch-folk-theorem-demo.streamlit.app/) und [tit-for-tat-demo](https://sebastianhanisch-tit-for-tat-demo.streamlit.app/):
dort läuft die Beziehung unbeschränkt weiter, hier ist sie **endlich** und das Ende ist bekannt. Die Kante ist ein `kontrast` (dieselbe Frage, anderer Horizont).

Vehikel: ein Rahmenvertrag über N Wochen zwischen zwei Spediteuren (Auszahlungen 5/3/1/0, gewählt). Eigennutz und Rationalität sind Modellannahmen.

## Warum dieses Problem

Wer weiß, dass es zu Ende ist, hat in der letzten Runde nichts mehr zu verlieren. Die Rückwärtsinduktion treibt das bis zur ersten Runde. Die Demo zeigt, **wie groß der
Anreiz tatsächlich ist, was Unsicherheit über das Ende daran ändert, und warum es nicht aufs Wissen, sondern auf ein spätestes Ende ankommt**.

## Modell

Das Gefangenendilemma 5/3/1/0 über N Runden. **Tit-for-Tat, am Ende defektierend (TFT-Dk)** spielt wie Tit-for-Tat, defektiert aber in den letzten k Runden immer; k = 0 ist
gewöhnliches Tit-for-Tat, k = N ist Immer-Defektieren. Die **beste Antwort** auf einen reaktiven Gegner wird exakt per Rückwärtsrechnung über die eigene Vorrunden-Aktion
bestimmt. Bei zufälligem Ende (gleichverteilt über N bis N + w) kommt die Gefahrenrate je Runde hinzu.

## Methodik

- **Beste Antwort:** `best_response`: Rückwärtsrechnung über (Runde, eigene Vorrunden-Aktion).
- **Kette:** `best_response_chain`: beste Antwort auf TFT-Dk für k = 0 … N.
- **Zufälliges Ende:** `random_horizon_best_response`: Gefahrenrate h_t = P(T = t | T ≥ t).
- **Unbeschränktes Ende:** `geometric_gain`: Wertiteration bei Fortsetzungswahrscheinlichkeit δ.

## Befunde (gemessen, keine Behauptungen)

Auszahlungen 5/3/1/0.

| Frage | Befund | Test |
|---|---|---|
| Wie groß ist der Vorteil des letzten Zuges gegen Tit-for-Tat? | **Genau 2 Punkte, für jede Länge ab einer Runde**: Kooperieren bis Runde N − 1, in Runde N defektieren, Wert 3N + 2. Je Runde 2/N. | `test_the_gain_of_the_best_response_is_exactly_two_for_every_length`, `test_best_response_matches_full_enumeration` |
| Was ist die Kette der besten Antworten? | Auf TFT-Dk antwortet man mit TFT-D(k+1): eine Runde früher defektieren. Bei N = 10 beginnt die beste Antwort in Runde 10, 9, 8, …, 1 und bleibt bei Immer-Defektieren; die Werte sinken von 32 auf 10. | `test_best_response_chain_at_n_10` |
| Gleichgewichte des Zwei-Runden-Spiels | Aufzählung aller 32 × 32 reinen Strategien: alle Nash-Gleichgewichte haben (2 / 2) und defektieren auf dem Pfad in beiden Runden. | `test_two_round_game_has_a_unique_equilibrium_payoff_by_enumeration` |
| Was kostet das bekannte Ende? | Bei N = 10 bekommt jeder im Gleichgewicht 10 statt 30, also 20 weniger. | `test_equilibrium_value_at_n_10` |
| Bekanntes Ende gegen unbeschränktes mit gleicher erwarteter Dauer | Bei unbeschränktem Ende (δ = 1 − 1/N) ist Tit-for-Tat ab N = 3 (δ = 2/3) ein **exaktes** Gleichgewicht, bei N = 2 liegt der Vorteil bei 0,33 je Runde. Bei bekanntem Ende bleibt er 2/N. | `test_unbounded_end_with_the_same_expected_length` |
| Zufälliges Ende gleichverteilt über N bis N + w | Die beste Antwort defektiert erst in der **spätestmöglichen** Runde N + w, der Vorteil ist **2/(w + 1)**: 2 / 1 / 0,67 / 0,33 / 0,18 / 0,095 / 0,049 bei w = 0 / 1 / 2 / 5 / 10 / 20 / 40. | `test_random_horizon_numbers`, `test_random_horizon_matches_full_enumeration` |

### Befunde gegenüber dem Plan

Der Plan erwartete „Vorteil des Defektierens zum Ende in Abhängigkeit von N“. Gerechnet ist es schärfer: **der Vorteil ist unabhängig von N genau 2**; nur je Runde sinkt er mit
1/N. Außerdem zeigt die Rechnung mit zufälligem Ende, dass **Unsicherheit** den Anreiz klein macht (2/(w + 1)), ihn aber nicht beseitigt, solange es ein spätestes mögliches Ende
gibt; aufgehoben wird er erst, wenn das Ende **unbeschränkt** ist.

## Ehrliche Grenzen

- **Gemeinsames Wissen über das Ende und über die Rationalität des anderen:** bei Zweifeln kann sich Kooperation lohnen (Kreps u. a. 1982), nicht modelliert.
- **Die Rechnung sagt, was rational wäre**, nicht, was Menschen tun; das ist empirisch und hier nicht untersucht.
- **Auszahlungen gewählt:** der Betrag 2 hängt an T − R.
- **Gegner reaktiv:** beste Antworten gegen Strategien mit kurzem Gedächtnis; gegen andere gelten dieselben Aussagen, die Rechnung wäre größer.
- **Stufenspiel mit nur einem Gleichgewicht:** hätte es mehrere, ließe sich Kooperation früher mit Drohungen stützen (Benoit/Krishna 1985).

## Verifikation

- **Kern:** je Einheit eine Handrechnung (Aktionen von TFT-Dk, beste Antworten für N = 1, 2, 3, Kette, zufälliges Ende, Schwelle 2/3, Rückwärtsinduktions-Tabelle).
- **Orakel** (`tests/test_oracle_endliche_horizonte.py`): (1) die beste Antwort gegen Aufzählung aller 2^N Aktionsfolgen (N bis 12); (2) die Nash-Gleichgewichte des Zwei-Runden-Spiels
  durch Aufzählung aller 32 × 32 reinen Strategien; (3) das zufällige Ende gegen Aufzählung aller Aktionsfolgen mit Erwartungswert über die Länge; (4) der Vorteil bei
  unbeschränktem Ende gegen die geschlossene Form aus den drei Kandidaten (Kooperieren, Immer-D, Abwechseln).
- **Claims:** jede Zahl dieses READMEs in `tests/test_claims.py`.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, Permalink begrenzt, Strategien erklärt) und Footer-Test.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `ehz_algorithm.py` | Kern: beste Antwort, Kette, zufälliges Ende, unbeschränktes Ende |
| `ehz_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `ehz_evaluation.py` | Analyse, Kurven, Strategieübersicht, Verdikt |
| `ehz_presets.py` | Permalink (Begrenzen), Presets |
| `ehz_scenario.py` | Das Spiel und TFT-Dk |
| `ehz_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handrechnung, Orakel, Claims, Presets, AppTest-Smoke-Test, Footer |

## Bewusst nicht umgesetzt

- **Unvollständige Information und Reputation** (Kreps/Milgrom/Roberts/Wilson): eigenes Modell mit einem Typ „Tit-for-Tat-Spieler“.
- **Mehrere Gleichgewichte im Stufenspiel:** andere Spiele.
- **Experimente mit Menschen:** keine Daten in dieser Demo.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
