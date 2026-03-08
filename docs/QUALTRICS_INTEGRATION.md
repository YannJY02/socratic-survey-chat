# Qualtrics Integration Guide

This guide explains how to connect the Qualtrics pre-test and post-test surveys with the Streamlit Socratic AI Tutor application using participant IDs.

## Overview

The experiment flow uses a participant ID (`pid`) to link data across three stages:

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Pre-Test    │  pid ──► │  Streamlit   │  pid ──► │  Post-Test   │
│  (Qualtrics) │         │  AI Chat     │         │  (Qualtrics) │
└──────────────┘         └──────────────┘         └──────────────┘
```

1. The pre-test survey generates or receives a `pid` for each participant.
2. On completion, Qualtrics redirects the participant to the Streamlit app with `?pid=XXXX` in the URL.
3. The Streamlit app reads the `pid`, logs the conversation under that ID, and on session end redirects to the post-test survey with `?pid=XXXX`.
4. The post-test survey captures the `pid` for matching.

All three data sources (pre-test responses, chat logs, post-test responses) can be joined on the `pid` field during analysis.

## Pre-Test Survey Setup

### 1. Create an Embedded Data Field

The `pid` field must be defined in the Qualtrics Survey Flow so it can be used in the redirect URL.

1. Open your pre-test survey in Qualtrics.
2. Go to **Survey Flow** (left sidebar or top menu).
3. Click **Add a New Element Here** at the top of the flow (before any question blocks).
4. Select **Embedded Data**.
5. Add a field named `pid`.
6. Set its value to a unique identifier. You have two options:

**Option A: Auto-generate a random ID**

Set the value to `${e://Field/ResponseID}`. This uses the Qualtrics-generated unique response ID as the participant ID.

**Option B: Pass a pre-assigned ID**

If you distribute unique links to participants (e.g., from a participant list), you can pass the `pid` as a URL parameter when sending the survey link:

```
https://your-university.qualtrics.com/jfe/form/SV_XXXXXXXXXX?pid=PARTICIPANT_001
```

In this case, leave the Embedded Data value blank — Qualtrics will automatically populate it from the URL parameter.

### 2. Configure the End-of-Survey Redirect

After the participant completes the pre-test, Qualtrics must redirect them to the Streamlit application with the `pid` in the URL.

1. In **Survey Flow**, click **Add a New Element Here** at the end of the flow (after all question blocks).
2. Select **End of Survey**.
3. Check **Redirect to a URL**.
4. Enter the Streamlit app URL with the `pid` piped in:

```
http://localhost:8501/?pid=${e://Field/pid}
```

If deploying on a server, replace `localhost:8501` with the server address.

5. Click **Apply**.

### Survey Flow Summary (Pre-Test)

Your pre-test Survey Flow should look like this:

```
┌─────────────────────────────────────────────┐
│  Embedded Data                              │
│    pid = ${e://Field/ResponseID}            │
├─────────────────────────────────────────────┤
│  Block: Consent Form                        │
├─────────────────────────────────────────────┤
│  Block: Demographics                        │
├─────────────────────────────────────────────┤
│  Block: Pre-Test Questions                  │
├─────────────────────────────────────────────┤
│  End of Survey                              │
│    ✓ Redirect to URL:                       │
│    http://localhost:8501/?pid=${e://Field/pid}│
└─────────────────────────────────────────────┘
```

## Post-Test Survey Setup

### 1. Create an Embedded Data Field

The post-test survey must capture the `pid` passed from the Streamlit app.

1. Open your post-test survey in Qualtrics.
2. Go to **Survey Flow**.
3. Add an **Embedded Data** element at the top of the flow.
4. Add a field named `pid`.
5. Leave the value **blank**. Qualtrics will automatically populate it from the `?pid=XXXX` URL parameter when the participant is redirected from the Streamlit app.

### 2. No Redirect Needed

The post-test survey is the final step. You can configure a standard end-of-survey message (e.g., "Thank you for participating") without any redirect.

### Survey Flow Summary (Post-Test)

```
┌─────────────────────────────────────────────┐
│  Embedded Data                              │
│    pid = (blank, populated from URL)        │
├─────────────────────────────────────────────┤
│  Block: Post-Test Questions                 │
├─────────────────────────────────────────────┤
│  Block: Debrief / Feedback (optional)       │
├─────────────────────────────────────────────┤
│  End of Survey                              │
│    "Thank you for participating."           │
└─────────────────────────────────────────────┘
```

## Streamlit App Configuration

The Streamlit app reads the `pid` from the URL query parameter and passes it to the post-test survey on redirect. This is handled automatically by the application code.

In your `.env` file, set the post-test survey URL:

```
POST_SURVEY_URL=https://your-university.qualtrics.com/jfe/form/SV_YYYYYYYYYY
```

The app will redirect participants to:

```
https://your-university.qualtrics.com/jfe/form/SV_YYYYYYYYYY?pid=XXXX
```

where `XXXX` is the participant's ID from the session.

## Testing the Full Flow

Before running the experiment with real participants, test the entire flow:

1. Start the Streamlit app locally (see [SETUP_GUIDE.md](SETUP_GUIDE.md)).

2. Open the pre-test survey in preview mode. Complete it and verify that:
   - You are redirected to the Streamlit app.
   - The URL contains `?pid=...` with the expected value.

3. In the Streamlit app, send a few messages and then end the session. Verify that:
   - A log file is created in `logs/` with the `pid` in the filename.
   - You are redirected to the post-test survey with `?pid=...` in the URL.

4. Complete the post-test survey and verify that:
   - The `pid` value appears in the survey response data when exported.

5. Export both surveys from Qualtrics and confirm the `pid` column is present and matches across datasets.

## Matching Data for Analysis

After data collection, you will have three data sources to combine:

| Source | Format | Key Field |
|--------|--------|-----------|
| Pre-test survey | Qualtrics CSV export | `pid` |
| Chat logs | JSON files in `logs/` | `pid` (in filename and file content) |
| Post-test survey | Qualtrics CSV export | `pid` |

### Export Chat Logs

Use the provided export script to convert chat logs into a CSV file:

```bash
source .venv/bin/activate
python scripts/export_logs.py
```

This creates a CSV file in the `data/` directory with columns including `pid`, message content, timestamps, and message roles.

### Merge Datasets

In your analysis environment (Python, R, or similar), merge the three datasets on the `pid` column:

**Python (pandas) example:**

```python
import pandas as pd

pre_test = pd.read_csv("qualtrics_pretest_export.csv")
post_test = pd.read_csv("qualtrics_posttest_export.csv")
chat_logs = pd.read_csv("data/chat_logs.csv")

# Merge pre-test and post-test
combined = pre_test.merge(post_test, on="pid", suffixes=("_pre", "_post"))

# Aggregate chat data per participant (e.g., number of messages, session duration)
chat_summary = chat_logs.groupby("pid").agg(
    num_messages=("message", "count"),
    session_duration=("timestamp", lambda x: x.max() - x.min())
).reset_index()

# Merge with survey data
full_dataset = combined.merge(chat_summary, on="pid", how="left")
```

### Handling Missing Data

- If a `pid` appears in the pre-test but not in chat logs, the participant may have dropped out before starting the chat.
- If a `pid` appears in chat logs but not in the post-test, the participant may have left during or after the chat without completing the post-test.
- Use the `how="outer"` parameter in pandas merge to identify all such cases for reporting attrition.

## Qualtrics Tips

- **Preview vs. Publish:** Test the full flow using Qualtrics preview mode first. Published surveys generate real response data.
- **Anonymous links:** When distributing the pre-test, use an anonymous link if you do not need to track individual invitations. The `pid` (via `ResponseID`) will still be unique.
- **Response export:** When exporting from Qualtrics, select "Download Data Table" in CSV format. Make sure the `pid` embedded data field is included in the export columns.
- **URL encoding:** Qualtrics handles URL encoding of the `pid` value automatically. No manual encoding is needed.
