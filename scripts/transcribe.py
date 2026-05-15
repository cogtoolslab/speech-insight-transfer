#!/usr/bin/env python3
"""Transcribe participant trial audio with WhisperX.

Expected input layout:

    data/recordings/
      sub_abc123/
        trial_1.wav
        trial_2.wav

By default, outputs are written next to each audio file as
``trial_N_transcription_whisperX.json``. The JSON includes the final text under
``without_timestamps.text`` so it can be consumed by the analysis notebook.
"""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path


def default_recordings_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "recordings"


def choose_device(requested: str) -> str:
    if requested != "auto":
        return requested
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def choose_compute_type(requested: str, device: str) -> str:
    if requested != "auto":
        return requested
    return "float16" if device.startswith("cuda") else "int8"


def clear_memory(device: str) -> None:
    import torch

    gc.collect()
    if device.startswith("cuda") and torch.cuda.is_available():
        torch.cuda.empty_cache()


def format_segments(segments: list[dict]) -> list[dict]:
    return [
        {
            "text": segment.get("text", ""),
            "start": segment.get("start"),
            "end": segment.get("end"),
        }
        for segment in segments
    ]


def joined_text(segments: list[dict]) -> str:
    return "".join(segment.get("text", "") for segment in segments)


def output_path_for(audio_path: Path, suffix: str) -> Path:
    return audio_path.with_name(f"{audio_path.stem}{suffix}")


def discover_audio_files(recordings_dir: Path, pattern: str) -> list[Path]:
    if not recordings_dir.exists():
        raise FileNotFoundError(f"Recordings directory does not exist: {recordings_dir}")
    return sorted(path for path in recordings_dir.glob(f"*/{pattern}") if path.is_file())


def write_output(
    output_path: Path,
    audio_path: Path,
    segments: list[dict],
    *,
    aligned_segments: list[dict] | None = None,
) -> None:
    base_text = joined_text(segments)
    timestamp_segments = aligned_segments if aligned_segments is not None else segments

    output = {
        "file": str(audio_path),
        "with_timestamps": {
            "text": joined_text(timestamp_segments),
            "segments": format_segments(timestamp_segments),
        },
        "without_timestamps": {
            "text": base_text,
        },
    }

    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")


def transcribe_audio_files(args: argparse.Namespace) -> None:
    try:
        import whisperx
    except ImportError as exc:
        raise SystemExit(
            "This script requires whisperx. Install it before running transcription."
        ) from exc

    recordings_dir = args.recordings_dir.expanduser().resolve()
    audio_files = discover_audio_files(recordings_dir, args.pattern)
    device = choose_device(args.device)
    compute_type = choose_compute_type(args.compute_type, device)
    download_root = str(args.model_dir.expanduser().resolve()) if args.model_dir else None

    print(f"Recordings directory: {recordings_dir}")
    print(f"Found {len(audio_files)} audio files matching {args.pattern!r}")
    print(f"Device: {device}; compute_type: {compute_type}; model: {args.model_size}")

    model = whisperx.load_model(
        args.model_size,
        device=device,
        compute_type=compute_type,
        download_root=download_root,
        language=args.language,
    )

    pending_alignment: list[tuple[Path, Path, list[dict]]] = []
    for audio_path in audio_files:
        output_path = output_path_for(audio_path, args.output_suffix)
        if output_path.exists() and not args.overwrite:
            print(f"Skipping existing output: {output_path}")
            continue

        try:
            print(f"Transcribing {audio_path}")
            audio = whisperx.load_audio(str(audio_path))
            result = model.transcribe(audio, batch_size=args.batch_size)
            segments = result.get("segments", [])

            if args.skip_alignment:
                write_output(output_path, audio_path, segments)
                print(f"Saved {output_path}")
            else:
                pending_alignment.append((audio_path, output_path, segments))
        except Exception as exc:
            print(f"Error transcribing {audio_path}: {exc}")

    del model
    clear_memory(device)

    if args.skip_alignment or not pending_alignment:
        return

    align_model, metadata = whisperx.load_align_model(language_code=args.language, device=device)
    for audio_path, output_path, segments in pending_alignment:
        try:
            print(f"Aligning {audio_path}")
            audio = whisperx.load_audio(str(audio_path))
            aligned = whisperx.align(
                segments,
                align_model,
                metadata,
                audio,
                device=device,
                return_char_alignments=False,
            )
            write_output(
                output_path,
                audio_path,
                segments,
                aligned_segments=aligned.get("segments", []),
            )
            print(f"Saved {output_path}")
        except Exception as exc:
            print(f"Error aligning {audio_path}: {exc}")

    del align_model
    clear_memory(device)


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
        default="trial_*.wav",
        help="Audio filename pattern to process within each participant folder.",
    )
    parser.add_argument(
        "--output-suffix",
        default="_transcription_whisperX.json",
        help="Suffix appended to each audio stem for the output JSON.",
    )
    parser.add_argument("--model-size", default="large-v2", help="WhisperX model size.")
    parser.add_argument("--batch-size", type=int, default=16, help="WhisperX batch size.")
    parser.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cuda", "cpu"],
        help="Device to use. Defaults to CUDA when available.",
    )
    parser.add_argument(
        "--compute-type",
        default="auto",
        help="WhisperX compute type. Defaults to float16 on CUDA and int8 on CPU.",
    )
    parser.add_argument("--language", default="en", help="Language code for transcription/alignment.")
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=None,
        help="Optional directory for downloaded WhisperX models.",
    )
    parser.add_argument(
        "--skip-alignment",
        action="store_true",
        help="Skip WhisperX alignment and write coarse transcription timestamps only.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing transcription JSON files.",
    )
    return parser.parse_args()


def main() -> None:
    transcribe_audio_files(parse_args())


if __name__ == "__main__":
    main()
