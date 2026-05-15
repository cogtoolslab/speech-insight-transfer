# speech-insight-transfer

Code and anonymized data for:

[**Linas Nasvytis, Judith E. Fan, "Leveraging Speech to Identify Signatures of Insight and Transfer in Problem Solving" (2026)**](https://arxiv.org/abs/2605.12970)

To be presented at CogSci 2026.

This project analyzes speech and behavioral data from a matchstick-arithmetic problem-solving experiment. Participants talked aloud while solving five problems, allowing us to study how performance, speech dynamics, semantic content, and reasoning moves change around successful solutions and transfer.

## Repository Structure

- `analysis/`  
  Main analysis notebooks and reports. `analysis_R.Rmd` contains the mixed-effects models for behavioral, speech-density, and speech-rate analyses. `analysis_python.ipynb` contains the additional behavioral summaries, semantic classifier analyses, reasoning-move analyses, and figure-generation code.

- `data/`  
  Anonymized project data used by the analyses.
  - `performance/`: trial-level behavioral data.
  - `recordings/`: per-participant transcription and speech/silence annotation files.
  - `speech_density/`: trial-level and temporal-bin speech-density tables.
  - `speech_rate/`: trial-level speech-rate table.
  - `speech_semantics/`: utterance embeddings and semantic-classifier outputs.
  - `reasoning_moves/`: utterance-level reasoning-move annotations.
  - `stimuli/`: matchstick-arithmetic stimuli and accepted outputs used in the experiment.

- `scripts/`  
  Optional helper scripts for generating transcripts with WhisperX and detecting speech/silence segments with Silero VAD. These scripts are not required to run the included analyses, but may help for researchers interested in applying similar analysis from raw audio recordings.
