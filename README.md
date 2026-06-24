# AITA Verdict Compass

TakeMeter project for predicting whether `r/AmItheAsshole` will mainly blame the poster.

## Community Choice

I chose `r/AmItheAsshole` because it is built around community judgment. People post real interpersonal conflicts, and the community decides whether the poster was wrong. That makes it a good text-classification task: the labels are grounded in the community, but the reasoning is still subjective and messy.

## Label Taxonomy

I used 2 labels, which fits the assignment's 2-4 label requirement.

| Label | Definition |
| --- | --- |
| `poster_not_blamed` | The original verdict was `NTA` or `NAH`; the community did not mainly blame the poster. |
| `poster_blamed` | The original verdict was `YTA` or `ESH`; the community blamed the poster or said the poster shared blame. |

Examples:

| Label | Example 1 | Example 2 |
| --- | --- | --- |
| `poster_not_blamed` | A poster refuses to lend a car to someone who previously crashed it and never paid. | A poster blocks a relative who keeps posting private health details publicly. |
| `poster_blamed` | A poster reads their partner's private messages because they feel insecure. | A poster escalates a conflict and then refuses to apologize even though both people behaved badly. |

## Dataset

Source: public `iterative/aita_dataset` dataset: https://github.com/iterative/aita_dataset

I used `aita_clean.csv`, which includes AITA title, body, verdict, score, and comment count. I mapped `NTA`/`NAH` to `poster_not_blamed` and `YTA`/`ESH` to `poster_blamed`. I used title + body as model input. Comments were not used as input.

| Label | Count |
| --- | ---: |
| `poster_blamed` | 2000 |
| `poster_not_blamed` | 2000 |
| **Total** | 4000 |

## Difficult Labeling Cases

| Post Excerpt | Final Label | Decision |
| --- | --- | --- |
| A post about not reporting sexual harassment. | `poster_not_blamed` | The topic sounds blame-heavy, but the mapped community verdict did not mainly blame the poster. |
| A post about refusing to let a minor cousin smoke shisha. | `poster_not_blamed` | It could look controlling, but the community treated it as a reasonable boundary. |
| A post about refusing to reconcile with an estranged father after a family death. | `poster_not_blamed` | Family-obligation language makes this borderline, but the community verdict sided with the poster. |

## Fine-Tuning Approach

The submitted local model is a TF-IDF + logistic regression text classifier trained on the balanced AITA dataset. The starter notebook still contains the DistilBERT path, but the local model was used for the final emergency run because it trained quickly and powers the demo app.

Key training decision: I switched from four labels to two labels after the four-way classifier performed poorly. The binary blame taxonomy is less detailed but more reliable and still grounded in AITA norms.

## Baseline

The baseline is a majority/random-style baseline on the same balanced test split, which is 50% because the dataset is balanced. Earlier I also ran Groq on the four-label version, but the final report uses the same binary test split as the trained model.

## Evaluation Report

| Model | Accuracy |
| --- | ---: |
| Baseline | 0.500 |
| Trained classifier | 0.587 |

Baseline:

| Label | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| `poster_blamed` | 0.500 | 1.000 | 0.667 |
| `poster_not_blamed` | 0.000 | 0.000 | 0.000 |

Trained classifier:

| Label | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| `poster_blamed` | 0.583 | 0.607 | 0.595 |
| `poster_not_blamed` | 0.590 | 0.567 | 0.578 |

Confusion matrix:

| True \ Predicted | `poster_blamed` | `poster_not_blamed` |
| --- | ---: | ---: |
| `poster_blamed` | 182 | 118 |
| `poster_not_blamed` | 130 | 170 |

## Error Analysis

| Post Excerpt | True Label | Predicted Label | Confidence | Analysis |
| --- | --- | --- | ---: | --- |
| WIBTA if I went on vacation with my own money? | `poster_blamed` | `poster_not_blamed` | 0.793 | The model saw independence/money language and treated it as reasonable, but the community blamed the poster in context. |
| AITA for wanting my partner to join our travel group text? | `poster_blamed` | `poster_not_blamed` | 0.721 | The model missed the controlling behavior implied by the full situation. |
| AITA for getting upset at my boyfriend because he did not want to watch a movie? | `poster_not_blamed` | `poster_blamed` | 0.716 | The model over-read ordinary relationship conflict as poster blame. |

Main pattern: the model is still shallow. It catches some blame/not-blame language, but it misses context where the community's judgment depends on social expectations rather than obvious keywords.

## Sample Classifications

| Post Excerpt | Predicted Label | Confidence | Notes |
| --- | --- | ---: | --- |
| AITA for playing a game while my mother is sick from cancer? | `poster_not_blamed` | 0.780 | Correct. |
| AITA for giving my ex-girlfriend a better present than my current girlfriend? | `poster_blamed` | 0.757 | Correct. |
| AITA for asking for my couch back? | `poster_blamed` | 0.756 | Correct. |
| AITA for refusing to cut my hair/beard for my sister's wedding? | `poster_not_blamed` | 0.748 | Correct. |
| WIBTA if I went on vacation with my own money? | `poster_not_blamed` | 0.793 | Incorrect; true label was `poster_blamed`. |

## Confidence Calibration

| Confidence Bucket | Examples | Accuracy | Average Confidence |
| --- | ---: | ---: | ---: |
| 0.00-0.60 | 431 | 0.559 | 0.547 |
| 0.60-0.80 | 169 | 0.657 | 0.649 |
| 0.80-1.00 | 0 | 0.000 | 0.000 |

Higher confidence generally corresponded to higher accuracy, so confidence was somewhat meaningful.

## Reflection

The model learned broad blame cues, not deep moral reasoning. It improved over a 50% baseline, but it still misses cases where AITA judgment depends on hidden context, relationship expectations, or whether a boundary was reasonable.

## Spec Reflection

The spec helped me avoid leakage: I kept verdicts and comments out of the model input.

The implementation diverged because I changed from four labels to two labels. The four-way version was too noisy and performed badly, so I used a simpler blame/not-blame taxonomy that still follows the assignment.

## AI Usage

I used AI to help design the label taxonomy, create validation/report scripts, and identify the final error pattern. I did not use AI-generated examples in the dataset. The examples come from the public AITA dataset.

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py --server.fileWatcherType none
```
