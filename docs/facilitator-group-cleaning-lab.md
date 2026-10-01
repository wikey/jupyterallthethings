# Facilitator guide: messy data, visible decisions

This guide supports `notebooks/05_group_data_cleaning_lab.ipynb`. Keep it off the shared screen until the group completes its first audit; it describes the planted issues and reference outcomes.

## Purpose

Participants should leave understanding that:

- cleaning is a sequence of substantive decisions, not a mechanical prelude;
- exact duplicates, multiple attempts, impossible values, and unusual-but-plausible values require different responses;
- normalization can mean label cleanup, unit conversion, or analytic standardization—and those operations are not interchangeable;
- subgroup differences can change when the outcome, standardization, exclusion policy, or adjustment set changes;
- regression adjustment does not turn observational demographic differences into causal effects; and
- an agent can implement and document choices without the participant needing to write Python.

## Suggested format: 75 minutes

| Time | Activity | Facilitation move |
| --- | --- | --- |
| 0–5 min | Frame the scenario | Emphasize synthetic data and “associations, not causes.” |
| 5–15 min | Stop 1: define a record | Ask participants to predict why row and student counts differ. |
| 15–25 min | Stop 2: normalize representation | Vote on missing values, category crosswalks, attendance units, and time source. |
| 25–40 min | Stop 3: investigate outliers | Show charts before exclusion; classify impossible, unusual, and contextual values. |
| 40–48 min | Select records | Agree on invalidated attempts and the ambiguous completed-retest policy. |
| 48–55 min | Stop 4: standardize | Contrast raw scale scores, growth, and within-grade z-scores. |
| 55–65 min | Stop 5: explore groups | Read economic, demographic, attendance, and time-of-day charts as questions. |
| 65–72 min | Stop 6: isolation ladder | Compare raw, standardized, adjusted, and sensitivity estimates. |
| 72–75 min | Decision log and exit question | Name one automated rule and one choice that must remain human. |

For a 45-minute session, omit the regression cell and use the comparison ladder as the final activity. For a 90-minute session, ask the group to change one policy and re-run all downstream cells.

## Before the session

1. Complete the Mac agent-assisted setup.
2. Open `notebooks/05_group_data_cleaning_lab.ipynb` by double-clicking it.
3. Select **Kernel → Restart Kernel and Clear Outputs** if you want discoveries to appear live rather than remain visible from the published reference run.
4. Keep this guide available on a private facilitator device.
5. Decide who will paste prompts into the local agent and who will record group decisions.

Do not regenerate the dataset immediately before the session. The committed CSV and saved notebook outputs are a tested pair.

## The planted data story

The file contains 240 synthetic students in Grades 6–8. The generator creates correlations among economic status, baseline score, attendance, MLL status, test scheduling, and targeted support. It does not assign a direct generated effect to race/ethnicity or gender. These design choices exist only to produce useful teaching patterns; they are not claims about real populations.

The Spring score generation includes prior score, grade, attendance, economic status, afternoon scheduling, device interruption, and targeted after-school support. Program participation is targeted rather than random, so a naive program comparison can make support look ineffective even when the generated contribution is positive.

### Planted record problems

| Issue | Reference count | Teaching point |
| --- | ---: | --- |
| Export rows | 254 | A file’s row count is not automatically its student count. |
| Distinct synthetic students | 240 | Intended analytic unit after a policy is chosen. |
| Exact duplicate rows | 5 | Safe to remove when every field is identical. |
| Students with non-identical multiple attempts | 9 | Requires attempt and status policy. |
| Invalidated first attempts with completed retests | 7 | Status provides a defensible selection rule. |
| Two completed attempts marked for policy review | 2 | There is no universal answer; document earliest/latest/local policy. |

### Planted representation problems

- 15 raw grade labels represent only Grades 6–8.
- Yes/no fields use values such as `Yes`, `Y`, `1`, `TRUE`, `No`, `N`, `0`, and `FALSE`.
- Gender and race/ethnicity contain capitalization, synonym, nonresponse, and whitespace variants.
- Attendance mixes proportions, whole percentages, percent strings, invalid values, and a missing marker.
- Scores and durations are stored as strings, sometimes with whitespace or text suffixes.
- Dates use ISO, slash, and written-month formats plus one impossible date.
- Start times use 12- and 24-hour formats plus missing markers.
- Ten source time-of-day labels conflict with a parseable start time.

### Planted value and context problems

| Flag after representation cleanup | Reference rows | Reference treatment |
| --- | ---: | --- |
| Fall score outside 100–800 | 1 | Invalid under documented operational range. |
| Spring score outside 100–800 | 2 | Invalid under documented operational range. |
| Growth outside 1.5×IQR fences | 6 before record selection | Flag, investigate, and retain in the primary analysis unless policy evidence says otherwise. |
| Duration under 10 minutes | 1 | Flag; do not infer cause automatically. |
| Duration over 180 minutes | 2 | Interpret with administration type/accommodation context. |
| Invalidated record status | 7 | Prefer valid completed retest. |
| Time-label conflict | 10 | Reference path trusts parseable start time and retains a conflict flag. |

After exact-duplicate removal and the reference attempt policy, there are 240 selected student records, 230 usable operational score pairs, and 227 records in the sensitivity set that excludes IQR growth flags.

## Recommended reference decisions

These are defensible defaults, not the only acceptable answers.

1. **Unit of analysis:** one selected Spring administration per synthetic student.
2. **Exact duplicates:** remove.
3. **Invalidated attempts:** prefer a completed retest.
4. **Two completed attempts:** use the latest attempt for the reference run; require local policy in practice.
5. **Missing categories:** preserve as missing or explicitly not reported; never silently convert to “No.”
6. **Category crosswalks:** combine only documented synonyms. Preserve the canonical categories represented in the schema.
7. **Attendance:** convert documented percentages to proportions; set impossible values missing and retain a conversion/invalid flag.
8. **Time of day:** derive from a parseable start time, use the source label only as fallback, and flag disagreement.
9. **Score validity:** exclude score pairs outside the documented 100–800 operational range from score analysis.
10. **Statistical outliers:** retain plausible values in the primary result and compare a flagged-exclusion sensitivity result.
11. **Duration:** do not use a universal duration cutoff to exclude scores.
12. **Standardization:** create Fall and Spring z-scores within grade while retaining original scale scores and growth.
13. **Small groups:** suppress displayed summaries below 10.
14. **Claims:** use “difference” or “association,” not “effect,” unless a design supports causal inference.

## Patterns the group should notice

Reference outputs may vary only if the data or policy is changed.

### Economic background

- The unadjusted Spring-score gap is about **−18.4 points** for students marked economically disadvantaged versus those marked No.
- The raw growth gap is much smaller, about **−2.9 points**.
- The within-grade Spring z-score gap is about **−0.46 standard deviations**.
- Excluding IQR growth flags changes the growth gap to about **−1.4 points**.
- In the reference baseline-adjusted model, the economic coefficient changes direction and its uncertainty interval includes zero.

The lesson is not that one estimate is “the truth.” The estimands, assumptions, missingness, outliers, and adjustment choices differ.

### Time of day

- The unadjusted afternoon-minus-morning growth gap is about **−6.5 points**.
- Excluding IQR growth flags changes it to about **−4.9 points**.
- The reference adjusted association is about **−5.1 points**, with an uncertainty interval spanning zero.

Ask who is more likely to be scheduled in the afternoon and whether schedule assignment is plausibly random.

### Other visible patterns

- Device interruption has a clearer negative adjusted association in the synthetic model.
- Attendance is positively associated with growth, but its adjusted uncertainty is wide.
- Targeted after-school participation can look negative in a naive or adjusted observational comparison because participants were selected for support based on need. This is confounding by indication.
- Race/ethnicity and gender should be explored with sufficient-n suppression and without inventing a causal story. They were not given direct effects in the generator.

## Useful live variations

Ask the agent to implement one variation at a time and add it to the decision log.

### Earliest versus latest completed attempt

Change:

```python
COMPLETED_RETEST_POLICY = "earliest_completed_attempt"
```

Then re-run record selection onward. Ask whether the difference is large enough to matter and what real policy should govern.

### Include versus exclude IQR growth flags

Compare `analysis` with:

```python
analysis.loc[~analysis["growth_iqr_flag"]]
```

Ask whether an IQR rule establishes data error. It does not.

### Trust source time label versus parsed time

Ask the agent to create a second time-of-day field that trusts the source label, then compare time estimates. Do not overwrite the reference field; make the sensitivity explicit.

### Different standardization groups

Compare grade-only standardization with grade-by-season or no standardization. Ask which question each supports and whether small cells become unstable.

### Adjustment-set discussion

Have participants place candidate variables into three buckets:

- needed to define a fair comparison;
- possibly downstream of the characteristic being studied; and
- unavailable but important.

Do not let the agent choose the model solely from correlations.

## Facilitation language

Prefer:

- “What rule would we want applied next year?”
- “What evidence says this value is wrong rather than unusual?”
- “Who disappears under this exclusion?”
- “What changed: the data, the scale, the population, or the question?”
- “This association remains after accounting for the variables we selected.”

Avoid:

- “The algorithm found the bad data.”
- “Normalization made the groups comparable.”
- “Economic background caused the gap.”
- “Afternoon testing lowers scores.”
- “The program did not work.”

## Agent operating boundary

The local agent may write and execute code, inspect schema and aggregate diagnostics, and report suppressed summaries. It should not display student keys or rows, transmit CSV contents, label individuals as outliers, choose demographic crosswalks without approval, or make causal claims.

The final artifact should include the group’s decision log, an attrition table, primary and sensitivity results, and plain-language caveats beside every shared chart.
