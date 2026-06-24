# TakeMeter Planning: AITA Verdict Compass

## Community

I am using `r/AmItheAsshole` for this project. It works well for a classifier because the community is already organized around verdicts, but the reasoning behind those verdicts is still subjective and messy.

The final model predicts whether the community mainly blames the poster. I am not trying to build a morality judge. I am trying to predict how this specific community usually responds to a conflict.

## Labels

| Label | Meaning | Definition |
| --- | --- | --- |
| `poster_not_blamed` | NTA or NAH | The final verdict does not mainly blame the poster. |
| `poster_blamed` | YTA or ESH | The final verdict blames the poster or says the poster shares blame. |

## Example Posts

These are example-style posts I used to make sure the labels are distinct. They are not final dataset rows.

| Label | Example 1 | Example 2 |
| --- | --- | --- |
| `NTA` | "AITA for refusing to lend my car to my sister after she crashed it last time and never paid for repairs?" | "AITA for leaving dinner after my uncle kept making comments about my weight even after I asked him to stop?" |
| `YTA` | "AITA for telling my roommate she should move out because I do not like her boyfriend visiting, even though visits are allowed in our lease?" | "AITA for reading my partner's messages because I felt insecure and then confronting them about a private conversation?" |
| `NAH` | "AITA for not going to my friend's destination wedding because I cannot afford it, even though she is hurt?" | "AITA for asking my parents for quiet during finals week when they already planned a family gathering at home?" |
| `ESH` | "AITA for yelling at my neighbor after he blocked my driveway, even though I had also been parking in front of his house for weeks?" | "AITA for refusing to apologize after my friend insulted me, even though I made the first joke about something I knew bothered her?" |

## Hard Edge Cases

The hardest edge case is probably the "right idea, bad execution" post. For example, the poster might be allowed to set a boundary, but they might do it in a cruel or public way. That can make the difference between `NTA`, `YTA`, and `ESH`.

My decision rule is to use the final community verdict as the label, even when I personally disagree. If a post feels borderline, I will note why in the `notes` column instead of changing the label based on my own interpretation.

Other cases I want to watch for:

- conflicts where both sides did something wrong, but one side clearly started it,
- posts where the comments identify missing context,
- situations where the poster is technically allowed to do something but still violates a social norm,
- short posts where there is not enough context to understand motivation.

## Data Collection Plan

I will collect at least 200 public AITA posts with final verdicts. The input text will be the post title and body only. I will remove verdict flair, final result text, and anything copied from comments.

Target counts:

| Label | Target |
| --- | ---: |
| `NTA` | 50 |
| `YTA` | 50 |
| `NAH` | 50 |
| `ESH` | 50 |

CSV columns:

| Column | Use |
| --- | --- |
| `text` | Used by the notebook for training and testing. |
| `label` | The final AITA verdict. |
| `notes` | My notes for borderline examples. |
| `community_reason_summary` | My short summary of why the community seemed to vote that way. |

If `NAH` or `ESH` is hard to find, I will collect extra examples for those labels instead of letting the dataset become too imbalanced. No label should be more than 70% of the dataset.

## How I Will Use Comments

Comments will not go into the model. They are too likely to leak the answer because people often start with "NTA" or "YTA."

I will use comments only for my own analysis:

- to understand why the community chose a verdict,
- to write the `community_reason_summary`,
- to explain model mistakes in the README.

## Evaluation Metrics

I will report accuracy for the baseline and fine-tuned model, but I do not want to rely on accuracy alone. With four labels, the model could look okay overall while failing on a harder label like `NAH` or `ESH`.

Metrics I will include:

- overall accuracy,
- per-class precision, recall, and F1,
- confusion matrix,
- three wrong predictions with explanations,
- confidence calibration for the stretch feature.

The label pairs I expect to be most confusing are `NTA` vs. `ESH` and `YTA` vs. `ESH`, because shared blame is harder than one-sided blame.

## Definition of Success

For this project, I would consider the classifier successful if:

- fine-tuned accuracy is at least 0.65,
- it beats the Groq zero-shot baseline or there is a clear explanation for why it does not,
- no label has F1 below 0.45,
- the error analysis finds a real pattern instead of just listing random misses.

For an actual public tool, I would want stronger results than that, closer to 0.75 accuracy with better recall on `NAH` and `ESH`.

## AI Tool Plan

I plan to use AI in three limited ways:

1. Stress-test the labels by asking for borderline AITA-style examples between label pairs.
2. Check collected text for possible verdict leakage before training.
3. Look for patterns in the wrong predictions after the model is evaluated.

I will not blindly accept AI labels as ground truth. If I use AI to pre-label or review anything, I will manually check it and disclose that in the README.

## Stretch Features

I plan to attempt two stretch features:

- **Confidence calibration:** bucket predictions by confidence and compare confidence to actual accuracy.
- **Deployed interface:** make a small Streamlit app where someone can paste a post and see the predicted verdict plus confidence.
