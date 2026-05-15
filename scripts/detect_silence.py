#!/usr/bin/env python3
"""Detect speech and silence segments in participant trial audio.

Expected input layout:

    data/recordings/
      sub_abc123/
        trial_1_fixed.wav
        trial_2_fixed.wav

By default, outputs are written next to each audio file as
``trial_N_speech_annotated.json``, matching the filename used by the analysis
notebook.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def default_recordings_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "recordings"


def load_audio_for_vad(audio_path: Path, sample_rate: int):
    try:
        import torchaudio
    except ImportError as exc:
        raise SystemExit(
            "This script requires torchaudio. Install torch and torchaudio before running VAD."
        ) from exc

    waveform, original_sample_rate = torchaudio.load(str(audio_path))
    waveform = waveform.mean(dim=0, keepdim=True)
    if original_sample_rate != sample_rate:
        waveform = torchaudio.functional.resample(waveform, original_sample_rate, sample_rate)
    return waveform


def extract_trial_number(path: Path) -> int | None:
    """Extract trial number from names like trial_1.wav or trial_1_fixed.wav."""
    parts = path.stem.split("_")
    if len(parts) >= 2 and parts[0] == "trial" and parts[1].isdigit():
        return int(parts[1])
    return None


def format_segment(start: int, end: int, sample_rate: int) -> dict:
    return {
        "start": round(start / sample_rate, 3),
        "end": round(end / sample_rate, 3),
        "duration": round((end - start) / sample_rate, 3),
    }


def detect_speech_and_silence(
    audio_path: Path,
    *,
    participant_id: str,
    trial_number: int,
    model,
    get_speech_timestamps,
    sample_rate: int,
    min_silence_duration: float,
) -> dict:
    waveform = load_audio_for_vad(audio_path, sample_rate)
    speech_segments = get_speech_timestamps(waveform, model, sampling_rate=sample_rate)

    silences = []
    last_end = 0
    min_silence_samples = int(min_silence_duration * sample_rate)

    for segment in speech_segments:
        start = int(segment["start"])
        end = int(segment["end"])
        if start - last_end >= min_silence_samples:
            silences.append(format_segment(last_end, start, sample_rate))
        last_end = end

    total_len = waveform.shape[-1]
    if total_len - last_end >= min_silence_samples:
        silences.append(format_segment(last_end, total_len, sample_rate))

    return {
        "file": str(audio_path),
        "participant_id": participant_id,
        "trial_number": trial_number,
        "speech_segments": [
            format_segment(int(segment["start"]), int(segment["end"]), sample_rate)
            for segment in speech_segments
        ],
        "silence_segments": silences,
    }


def discover_audio_files(recordings_dir: Path, pattern: str) -> list[Path]:
    if not recordings_dir.exists():
        raise FileNotFoundError(f"Recordings directory does not exist: {recordings_dir}")
    return sorted(path for path in recordings_dir.glob(f"*/{pattern}") if path.is_file())


def output_path_for(audio_path: Path, trial_number: int, template: str) -> Path:
    return audio_path.with_name(template.format(trial_number=trial_number, stem=audio_path.stem))


def process_audio_files(args: argparse.Namespace) -> None:
    try:
        import torch
    except ImportError as exc:
        raise SystemExit(
            "This script requires torch. Install torch and torchaudio before running VAD."
        ) from exc

    recordings_dir = args.recordings_dir.expanduser().resolve()
    audio_files = discover_audio_files(recordings_dir, args.pattern)
    print(f"Recordings directory: {recordings_dir}")
    print(f"Found {len(audio_files)} audio files matching {args.pattern!r}")

    model, utils = torch.hub.load(
        repo_or_dir=args.repo,
        model=args.model,
        trust_repo=True,
        force_reload=args.force_reload,
    )
    get_speech_timestamps = utils[0]

    for audio_path in audio_files:
        trial_number = extract_trial_number(audio_path)
        if trial_number is None:
            print(f"Skipping unrecognized trial filename: {audio_path}")
            continue

        output_path = output_path_for(audio_path, trial_number, args.output_template)
        if output_path.exists() and not args.overwrite:
            print(f"Skipping existing output: {output_path}")
            continue

        try:
            print(f"Processing {audio_path}")
            vad_output = detect_speech_and_silence(
                audio_path,
                participant_id=audio_path.parent.name,
                trial_number=trial_number,
                model=model,
                get_speech_timestamps=get_speech_timestamps,
                sample_rate=args.sample_rate,
                min_silence_duration=args.min_silence_duration,
            )
            output_path.write_text(json.dumps(vad_output, indent=2), encoding="utf-8")
            print(f"Saved {output_path}")
        except Exception as exc:
            print(f"Error processing {audio_path}: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--recordings-dir",
        type=Path,
        default=default_recordings_dir(),
        help="Directory containing one subfolder per participant.",
    )
    parser.add_argument(
        "--pattern",
        default="trial_*_fixed.wav",
        help="Audio filename pattern to process within each participant folder.",
    )
    parser.add_argument(
        "--output-template",
        default="trial_{trial_number}_speech_annotated.json",
        help="Output filename template. Available fields: {trial_number}, {stem}.",
    )
    parser.add_argument("--sample-rate", type=int, default=16000, help="VAD sample rate.")
    parser.add_argument(
        "--min-silence-duration",
        type=float,
        default=0.1,
        help="Minimum silence duration, in seconds, to include in the output.",
    )
    parser.add_argument(
        "--repo",
        default="snakers4/silero-vad",
        help="Torch Hub repository for the VAD model.",
    )
    parser.add_argument("--model", default="silero_vad", help="Torch Hub model name.")
    parser.add_argument(
        "--force-reload",
        action="store_true",
        help="Force Torch Hub to redownload/reload the VAD model.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing speech annotation JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    process_audio_files(parse_args())


if __name__ == "__main__":
    main()
