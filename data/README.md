# Data Notes

Participant identifiers have been anonymized as `sub_...`.

## Performance

`performance/trials_df.csv` contains one row per participant trial.

Accuracy is scored from the final response present in the answer field at trial end. In rare cases, this means a trial is counted correct even when the participant did not click submit before the timeout. The `submission_attempts` column records explicit submitted attempts only; the `response` column records the final answer-field contents.

Columns:

- `participant_id`: anonymized participant identifier.
- `trial_number`: trial index within participant, from 1 to 5.
- `group`: numeric experimental group code; `1` = Same Type, `2` = Different Type.
- `task_type`: matchstick problem type.
- `input`: original equation shown to the participant.
- `response`: final answer-field contents at trial end.
- `true_output`: list of accepted correct answer strings.
- `rt`: response time in milliseconds.
- `is_correct`: whether `response` matched an accepted correct answer.
- `submission_attempts`: list of explicitly submitted attempts, including answer text, correctness, timestamp, and time from trial start.
- `total_submissions`: number of explicit submitted attempts.
- `group_label`: human-readable group label.
- `rt_seconds`: response time in seconds.

## Recordings

`recordings/` contains one folder per anonymized participant. Each folder contains trial-level transcript and speech/silence annotation JSON files.

Common files:

- `trial_N_transcription_whisperX.json`: WhisperX transcript output for trial `N`.
- `trial_N_speech_annotated.json`: speech and silence segments for trial `N`.

## Speech Density

`speech_density/speech_density_trial_level.csv` contains trial-level speech/silence measures.

Columns:

- `participant_id`: anonymized participant identifier.
- `group`: numeric experimental group code.
- `trial_number`: trial index within participant.
- `task_type`: matchstick problem type.
- `phase`: trial phase relative to first success.
- `is_correct`: trial correctness.
- `audio_duration_s`: usable trial audio duration in seconds.
- `speech_total_s`: total detected speech duration in seconds.
- `silence_total_s`: total detected silence duration in seconds.
- `speech_ratio_audio`: speech duration divided by audio duration.
- `lexical_total_s`: detected lexical speech duration in seconds.
- `nonlex_total_s`: detected non-lexical speech duration in seconds.
- `lexical_ratio_audio`: lexical speech duration divided by audio duration.
- `nonlex_ratio_audio`: non-lexical speech duration divided by audio duration.

`speech_density/speech_density_bin_level_K5.csv` contains speech density in five equal temporal bins per trial.

Columns:

- `participant_id`: anonymized participant identifier.
- `group`: numeric experimental group code.
- `trial_number`: trial index within participant.
- `task_type`: matchstick problem type.
- `phase`: trial phase relative to first success.
- `bin_idx`: temporal bin index, from 1 to 5.
- `speech_density`: proportion of the bin classified as speech.

## Speech Rate

`speech_rate/speech_rate_trial_level.csv` contains trial-level word-rate measures.

Columns:

- `participant_id`: anonymized participant identifier.
- `trial_number`: trial index within participant.
- `phase`: trial phase relative to first success.
- `group`: numeric experimental group code.
- `task_type`: matchstick problem type.
- `is_correct`: trial correctness.
- `word_count`: transcript word count for the trial.
- `rt_seconds`: response time in seconds.
- `audio_duration_s`: usable trial audio duration in seconds.
- `wps_rt`: words per second using response time as the denominator.
- `wps_audio`: words per second using audio duration as the denominator.
- `wps_used`: words per second value used in analyses.
- `wps_source`: denominator source used for `wps_used`.

## Speech Semantics

`speech_semantics/embeddings/utterance_level/openai_text_embedding_3_large_cleaned/` contains utterance-level semantic-embedding data.

Files:

- `utterance_metadata.parquet`: utterance metadata aligned row-by-row with the embedding matrix.
- `utterance_embeddings.npy`: utterance embedding matrix.
- `manifest.json`: embedding model and file metadata.

Metadata columns:

- `participant_id`: anonymized participant identifier.
- `trial_number`: trial index within participant.
- `utterance_idx`: utterance index.
- `utterance_text`: transcribed utterance text.
- `start_s`: utterance start time in seconds.
- `end_s`: utterance end time in seconds.
- `duration_s`: utterance duration in seconds.
- `input`: original equation shown to the participant.
- `problem_key`: problem identifier.
- `is_correct`: trial correctness.
- `group`: numeric experimental group code.
- `group_label`: human-readable group label.
- `task_type`: matchstick problem type.
- `phase`: trial phase relative to first success.
- `rt`: response time in milliseconds.
- `audio_duration_s`: usable trial audio duration in seconds.
- `word_count_trial`: transcript word count for the full trial.
- `file_wav`: source audio filename.
- `utterance_word_count`: utterance-level word count.

## Reasoning Moves

`reasoning_moves/reasoning_moves_patched.parquet` contains utterance-level reasoning-move annotations.

Columns:

- `idx`: utterance row index.
- `sentence`: utterance text.
- `start`: utterance start time in seconds.
- `end`: utterance end time in seconds.
- `label`: original reasoning-move label.
- `trace_id`: utterance trace identifier.
- `participant_id`: anonymized participant identifier.
- `trial_number`: trial index within participant.
- `move_label`: patched reasoning-move label used in analyses.
- `group`: numeric experimental group code.
- `task_type`: matchstick problem type.
- `phase`: trial phase relative to first success.
- `is_correct`: trial correctness.
- `rt`: response time in milliseconds.
- `rt_seconds`: response time in seconds.
- `audio_duration_s`: usable trial audio duration in seconds.
- `word_count`: trial-level word count.
- `first_success_trial`: participant's first correct trial, when applicable.
- `input`: original equation shown to the participant.
