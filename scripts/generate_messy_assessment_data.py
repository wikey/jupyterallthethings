#!/usr/bin/env python3
"""Generate the synthetic, deliberately messy dataset used by lesson 05.

The generator contains the answer key for planted quality issues. Do not run or
show this file before participants have completed their first-pass audit.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MessyAssessmentData.csv"
SCHEMA_OUTPUT = ROOT / "MessyAssessmentDataSchema.csv"
SEED = 20260930
N_STUDENTS = 240


def choose_variant(rng: np.random.Generator, canonical: str, variants: dict[str, list[str]]) -> str:
    choices = variants.get(canonical, [canonical])
    return str(rng.choice(choices))


def build_clean_students(rng: np.random.Generator) -> pd.DataFrame:
    student_number = np.arange(1, N_STUDENTS + 1)
    student_key = [f"S{number:03d}" for number in student_number]
    grade = rng.choice([6, 7, 8], N_STUDENTS, p=[0.38, 0.34, 0.28])
    gender = rng.choice(
        ["Female", "Male", "Nonbinary", "Not reported"],
        N_STUDENTS,
        p=[0.47, 0.46, 0.05, 0.02],
    )
    race_ethnicity = rng.choice(
        [
            "Asian",
            "Black/African American",
            "Hispanic/Latino",
            "Multiracial",
            "White",
            "Not reported",
        ],
        N_STUDENTS,
        p=[0.10, 0.23, 0.28, 0.08, 0.28, 0.03],
    )

    economically_disadvantaged = rng.random(N_STUDENTS) < 0.49
    mll_probability = 0.13 + 0.18 * economically_disadvantaged
    mll = rng.random(N_STUDENTS) < mll_probability
    iep = rng.random(N_STUDENTS) < 0.18
    latent_preparation = rng.normal(0, 1, N_STUDENTS)

    attendance_rate = (
        0.955
        - 0.052 * economically_disadvantaged
        - 0.022 * mll
        - 0.030 * iep
        + rng.normal(0, 0.025, N_STUDENTS)
    )
    attendance_rate = np.clip(attendance_rate, 0.72, 1.0)

    fall_score = (
        430
        + 24 * (grade - 6)
        + 36 * latent_preparation
        - 15 * economically_disadvantaged
        - 9 * mll
        - 12 * iep
        + rng.normal(0, 15, N_STUDENTS)
    )
    fall_score = np.clip(np.rint(fall_score), 250, 690).astype(int)

    afternoon_probability = (
        0.24
        + 0.16 * economically_disadvantaged
        + 0.08 * (grade == 8)
        + 0.05 * mll
    )
    afternoon = rng.random(N_STUDENTS) < afternoon_probability
    test_hour = np.where(
        afternoon,
        rng.choice([12, 13, 14], N_STUDENTS, p=[0.20, 0.50, 0.30]),
        rng.choice([8, 9, 10], N_STUDENTS, p=[0.35, 0.45, 0.20]),
    )
    test_minute = rng.choice([0, 10, 15, 20, 30, 40, 45, 50], N_STUDENTS)

    device_interruption = rng.random(N_STUDENTS) < (0.06 + 0.07 * afternoon)
    after_school_program = rng.random(N_STUDENTS) < (
        0.20 + 0.16 * economically_disadvantaged + 0.08 * (fall_score < 420)
    )
    administration_type = np.where(
        attendance_rate < 0.82,
        "Makeup",
        np.where(iep & (rng.random(N_STUDENTS) < 0.45), "Extended time", "Standard"),
    )

    duration_minutes = (
        54
        + 15 * iep
        + 7 * mll
        + 10 * device_interruption
        + 5 * (administration_type == "Makeup")
        + rng.normal(0, 9, N_STUDENTS)
    )
    duration_minutes = np.clip(np.rint(duration_minutes), 24, 125).astype(int)

    growth = (
        27
        + 0.055 * (465 - fall_score)
        + 32 * (attendance_rate - 0.90)
        - 2.0 * economically_disadvantaged
        - 4.5 * afternoon
        - 8.0 * device_interruption
        + 4.0 * after_school_program
        + rng.normal(0, 9, N_STUDENTS)
    )
    spring_score = np.clip(np.rint(fall_score + growth), 250, 760).astype(int)

    start_date = np.datetime64("2026-04-14")
    day_offsets = rng.integers(0, 38, N_STUDENTS)
    test_date = pd.to_datetime(start_date + day_offsets.astype("timedelta64[D]"))

    frame = pd.DataFrame(
        {
            "student_key": student_key,
            "grade": grade,
            "race_ethnicity": race_ethnicity,
            "gender": gender,
            "economically_disadvantaged": np.where(economically_disadvantaged, "Yes", "No"),
            "mll": np.where(mll, "Yes", "No"),
            "iep": np.where(iep, "Yes", "No"),
            "attendance_rate": attendance_rate,
            "fall_score": fall_score,
            "spring_score": spring_score,
            "test_date": test_date,
            "test_start_time": [f"{hour:02d}:{minute:02d}" for hour, minute in zip(test_hour, test_minute)],
            "time_of_day": np.where(afternoon, "Afternoon", "Morning"),
            "duration_minutes": duration_minutes,
            "device_interruption": np.where(device_interruption, "Yes", "No"),
            "administration_type": administration_type,
            "after_school_program": np.where(after_school_program, "Yes", "No"),
            "attempt": 1,
            "record_status": "Complete",
        }
    )
    return frame


def add_retests(frame: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    retest_indices = rng.choice(frame.index, size=7, replace=False)
    retests = []
    for position, index in enumerate(retest_indices):
        original = frame.loc[index].copy()
        frame.loc[index, "device_interruption"] = "Yes"
        frame.loc[index, "record_status"] = "Invalidated - interruption"
        frame.loc[index, "spring_score"] = int(original["spring_score"] - rng.integers(6, 17))

        retest = original.copy()
        retest["attempt"] = 2
        retest["record_status"] = "Complete"
        retest["device_interruption"] = "No"
        retest["administration_type"] = "Makeup"
        retest["test_date"] = pd.Timestamp(original["test_date"]) + pd.Timedelta(days=int(rng.integers(2, 8)))
        retest["test_start_time"] = str(rng.choice(["08:30", "09:15", "10:00", "13:15"]))
        hour = int(str(retest["test_start_time"]).split(":")[0])
        retest["time_of_day"] = "Morning" if hour < 12 else "Afternoon"
        retest["duration_minutes"] = int(np.clip(int(original["duration_minutes"]) + rng.integers(-4, 8), 25, 130))
        retest["spring_score"] = int(np.clip(int(original["spring_score"]) + rng.integers(-2, 7), 250, 760))
        retests.append(retest)

    # Two completed second attempts are deliberately ambiguous rather than invalidated.
    ambiguous_indices = rng.choice(frame.index.difference(retest_indices), size=2, replace=False)
    for index in ambiguous_indices:
        retest = frame.loc[index].copy()
        retest["attempt"] = 2
        retest["record_status"] = "Complete - review retest policy"
        retest["administration_type"] = "Makeup"
        retest["test_date"] = pd.Timestamp(retest["test_date"]) + pd.Timedelta(days=4)
        retest["spring_score"] = int(np.clip(int(retest["spring_score"]) + rng.integers(-5, 10), 250, 760))
        retests.append(retest)

    return pd.concat([frame, pd.DataFrame(retests)], ignore_index=True)


def make_messy(frame: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    messy = frame.copy()

    variants = {
        "grade": {
            6: ["6", "Grade 6", "6th", "06", " 6 "],
            7: ["7", "Grade 7", "7th", "07", " 7 "],
            8: ["8", "Grade 8", "8th", "08", " 8 "],
        },
        "gender": {
            "Female": ["Female", "F", "female", " Female "],
            "Male": ["Male", "M", "male", " Male "],
            "Nonbinary": ["Nonbinary", "Non-binary", "NB"],
            "Not reported": ["Not reported", "Not Reported", "Prefer not to say"],
        },
        "race_ethnicity": {
            "Asian": ["Asian", "asian"],
            "Black/African American": ["Black/African American", "Black", "African American"],
            "Hispanic/Latino": ["Hispanic/Latino", "Hispanic", "Latino/a"],
            "Multiracial": ["Multiracial", "Two or more races", "Multi-racial"],
            "White": ["White", "white"],
            "Not reported": ["Not reported", "Not Reported", "Declined"],
        },
        "yes_no": {
            "Yes": ["Yes", "Y", "yes", "1", "TRUE"],
            "No": ["No", "N", "no", "0", "FALSE", " No "],
        },
        "time_of_day": {
            "Morning": ["Morning", "AM", "a.m.", "morning"],
            "Afternoon": ["Afternoon", "PM", "p.m.", "After lunch"],
        },
    }

    messy["grade"] = [choose_variant(rng, int(value), variants["grade"]) for value in messy["grade"]]
    messy["gender"] = [choose_variant(rng, str(value), variants["gender"]) for value in messy["gender"]]
    messy["race_ethnicity"] = [
        choose_variant(rng, str(value), variants["race_ethnicity"])
        for value in messy["race_ethnicity"]
    ]
    for column in ["economically_disadvantaged", "mll", "iep", "device_interruption", "after_school_program"]:
        messy[column] = [choose_variant(rng, str(value), variants["yes_no"]) for value in messy[column]]
    messy["time_of_day"] = [
        choose_variant(rng, str(value), variants["time_of_day"])
        for value in messy["time_of_day"]
    ]

    # Scores arrive as strings, with whitespace and several missing/error markers.
    for column in ["fall_score", "spring_score"]:
        messy[column] = messy[column].astype(str)
        spaced = rng.choice(messy.index, size=18, replace=False)
        messy.loc[spaced, column] = messy.loc[spaced, column].map(lambda value: f" {value} ")
    for index, marker in zip(rng.choice(messy.index, 5, replace=False), ["", "NA", "N/A", "absent", "—"]):
        messy.loc[index, "fall_score"] = marker
    for index, marker in zip(rng.choice(messy.index, 4, replace=False), ["", "absent", "N/A", "—"]):
        messy.loc[index, "spring_score"] = marker

    outlier_indices = rng.choice(messy.index, 5, replace=False)
    messy.loc[outlier_indices[0], "spring_score"] = "999"       # impossible high
    messy.loc[outlier_indices[1], "spring_score"] = "-45"       # impossible low
    messy.loc[outlier_indices[2], "fall_score"] = "55"          # impossible baseline
    baseline = pd.to_numeric(messy.loc[outlier_indices[3], "fall_score"], errors="coerce")
    messy.loc[outlier_indices[3], "spring_score"] = str(int(min(790, baseline + 175)))
    baseline = pd.to_numeric(messy.loc[outlier_indices[4], "fall_score"], errors="coerce")
    messy.loc[outlier_indices[4], "spring_score"] = str(int(max(105, baseline - 245)))

    # Attendance mixes proportions, percentages, percent strings, and invalid values.
    messy["attendance_rate"] = messy["attendance_rate"].map(lambda value: f"{value:.3f}")
    percent_indices = rng.choice(messy.index, 24, replace=False)
    messy.loc[percent_indices, "attendance_rate"] = messy.loc[percent_indices, "attendance_rate"].map(
        lambda value: str(round(float(value) * 100, 1))
    )
    percent_string_indices = rng.choice(messy.index.difference(percent_indices), 5, replace=False)
    messy.loc[percent_string_indices, "attendance_rate"] = messy.loc[percent_string_indices, "attendance_rate"].map(
        lambda value: f"{round(float(value) * 100)}%"
    )
    invalid_attendance = rng.choice(
        messy.index.difference(percent_indices).difference(percent_string_indices), 3, replace=False
    )
    messy.loc[invalid_attendance, "attendance_rate"] = ["108%", "-0.20", "not recorded"]

    # Dates and start times use multiple export formats.
    date_values = pd.to_datetime(messy["test_date"])
    date_formats = rng.choice(["iso", "slash", "words"], len(messy), p=[0.45, 0.35, 0.20])
    messy["test_date"] = [
        date.strftime("%Y-%m-%d") if style == "iso"
        else date.strftime("%m/%d/%Y") if style == "slash"
        else date.strftime("%b %d, %Y")
        for date, style in zip(date_values, date_formats)
    ]
    messy.loc[rng.choice(messy.index, 1), "test_date"] = "2026-13-40"

    def mixed_time(value: str) -> str:
        hour, minute = [int(part) for part in value.split(":")]
        style = rng.choice(["24", "12", "spaced"])
        if style == "24":
            return f"{hour:02d}:{minute:02d}"
        suffix = "AM" if hour < 12 else "PM"
        hour12 = hour if 1 <= hour <= 12 else hour - 12
        if style == "12":
            return f"{hour12}:{minute:02d} {suffix}"
        return f" {hour12}:{minute:02d}{suffix.lower()} "

    messy["test_start_time"] = messy["test_start_time"].map(mixed_time)
    missing_times = rng.choice(messy.index, 5, replace=False)
    messy.loc[missing_times, "test_start_time"] = rng.choice(["", "not recorded"], len(missing_times))
    mismatch_times = rng.choice(messy.index.difference(missing_times), 10, replace=False)
    messy.loc[mismatch_times, "time_of_day"] = messy.loc[mismatch_times, "time_of_day"].map(
        lambda value: "Afternoon" if str(value).strip().lower() in {"morning", "am", "a.m."} else "Morning"
    )

    # Durations include text, missing values, and values requiring contextual review.
    messy["duration_minutes"] = messy["duration_minutes"].astype(str)
    minute_text = rng.choice(messy.index, 15, replace=False)
    messy.loc[minute_text, "duration_minutes"] = messy.loc[minute_text, "duration_minutes"] + " min"
    duration_issues = rng.choice(messy.index.difference(minute_text), 4, replace=False)
    messy.loc[duration_issues, "duration_minutes"] = ["4", "265", "420", ""]

    # A few demographic fields are unreported; missing is not equivalent to "No."
    for column, count in [
        ("economically_disadvantaged", 7),
        ("mll", 5),
        ("iep", 4),
        ("gender", 3),
        ("race_ethnicity", 4),
    ]:
        indices = rng.choice(messy.index, count, replace=False)
        messy.loc[indices, column] = rng.choice(["", "Unknown", "Not Reported"], count)

    # Add exact duplicate export rows after all formatting problems are introduced.
    duplicate_rows = messy.loc[rng.choice(messy.index, 5, replace=False)].copy()
    messy = pd.concat([messy, duplicate_rows], ignore_index=True)
    messy = messy.sample(frac=1, random_state=SEED).reset_index(drop=True)
    return messy


def write_schema() -> None:
    rows = [
        ("student_key", "Synthetic pseudonymous student key; not an anonymization method", "string", "One logical record per student after applying attempt policy"),
        ("grade", "Current enrolled grade", "category", "Expected grades 6, 7, or 8; labels are inconsistent"),
        ("race_ethnicity", "Synthetic reported race/ethnicity category", "category", "Labels require policy-aware normalization; some values are unreported"),
        ("gender", "Synthetic reported gender category", "category", "Labels require normalization; preserve nonresponse"),
        ("economically_disadvantaged", "Synthetic economic-disadvantage eligibility indicator", "category", "Yes/No/unknown represented inconsistently"),
        ("mll", "Synthetic multilingual-learner indicator", "category", "Yes/No/unknown represented inconsistently"),
        ("iep", "Synthetic individualized education program indicator", "category", "Yes/No/unknown represented inconsistently"),
        ("attendance_rate", "Year-to-date attendance", "numeric", "Mixed proportion, percentage, percent-string, missing, and invalid representations"),
        ("fall_score", "Fall mathematics scale score", "numeric", "Expected operational range 100–800; stored as messy strings"),
        ("spring_score", "Spring mathematics scale score", "numeric", "Expected operational range 100–800; stored as messy strings"),
        ("test_date", "Spring assessment administration date", "date", "Multiple date formats plus an invalid value"),
        ("test_start_time", "Local start time for the spring assessment", "time", "12-hour, 24-hour, missing, and whitespace variants"),
        ("time_of_day", "Source-system morning/afternoon label", "category", "Some labels conflict with parseable start times"),
        ("duration_minutes", "Recorded assessment duration in minutes", "numeric", "Text suffixes, missingness, and contextual outliers"),
        ("device_interruption", "Whether a device interruption was recorded", "category", "Yes/No represented inconsistently"),
        ("administration_type", "Standard, makeup, or extended-time administration", "category", "Use when interpreting duration and schedule"),
        ("after_school_program", "Synthetic participation in an after-school support program", "category", "Targeted participation; not randomly assigned"),
        ("attempt", "Administration attempt number", "integer", "Some students have multiple attempts"),
        ("record_status", "Completion or invalidation status", "category", "Use with attempt and local policy to select records"),
    ]
    pd.DataFrame(rows, columns=["column", "description", "intended_type", "cleaning_note"]).to_csv(
        SCHEMA_OUTPUT, index=False
    )


def main() -> None:
    rng = np.random.default_rng(SEED)
    clean = build_clean_students(rng)
    with_retests = add_retests(clean, rng)
    messy = make_messy(with_retests, rng)
    messy.to_csv(OUTPUT, index=False)
    write_schema()
    print(
        f"Wrote {len(messy):,} messy rows for "
        f"{messy['student_key'].nunique():,} synthetic students to {OUTPUT}"
    )


if __name__ == "__main__":
    main()
