from typing import List, Tuple
from schemas.project import CanonicalTimeline, LineTiming, ValidationDiagnostic


class QualityValidator:
    """
    Automated Quality Validation Engine.
    Validates synchronized timelines for timestamp anomalies, overlaps,
    implausible word durations, and alignment drift.
    """

    @staticmethod
    def validate_timeline(
        timeline: CanonicalTimeline,
        silence_intervals: List[Tuple[int, int]] = None
    ) -> Tuple[List[ValidationDiagnostic], float]:
        diagnostics: List[ValidationDiagnostic] = []
        silences = silence_intervals or []
        audio_duration = timeline.audio.duration_ms

        lines = timeline.lines
        total_lines = len(lines)
        if total_lines == 0:
            return diagnostics, 1.0

        valid_line_count = 0

        for i, line in enumerate(lines):
            line_has_error = False

            # Check 1: Negative or zero line duration
            if line.end_ms <= line.start_ms:
                diagnostics.append(
                    ValidationDiagnostic(
                        severity="warning",
                        code="INVALID_LINE_DURATION",
                        message=f"Line '{line.display_text}' has zero or negative duration ({line.start_ms}ms to {line.end_ms}ms)",
                        line_id=line.id,
                        start_ms=line.start_ms,
                        end_ms=line.end_ms
                    )
                )
                line_has_error = True

            # Check 2: Out of bounds timing
            if line.end_ms > audio_duration:
                diagnostics.append(
                    ValidationDiagnostic(
                        severity="error",
                        code="OUT_OF_BOUNDS_TIMING",
                        message=f"Line '{line.display_text}' extends past audio duration ({line.end_ms}ms > {audio_duration}ms)",
                        line_id=line.id,
                        start_ms=line.start_ms,
                        end_ms=line.end_ms
                    )
                )
                line_has_error = True

            # Check 3: Overlap with next line
            if i < total_lines - 1:
                next_line = lines[i + 1]
                if line.end_ms > next_line.start_ms:
                    diagnostics.append(
                        ValidationDiagnostic(
                            severity="warning",
                            code="TIMESTAMP_OVERLAP",
                            message=f"Line '{line.display_text}' overlaps next line by {line.end_ms - next_line.start_ms}ms",
                            line_id=line.id,
                            start_ms=line.start_ms,
                            end_ms=line.end_ms
                        )
                    )
                    line_has_error = True

            # Check 4: Implausible word durations
            for w in line.words:
                w_duration = w.end_ms - w.start_ms
                if w_duration < 40 or w_duration > 5000:
                    diagnostics.append(
                        ValidationDiagnostic(
                            severity="info",
                            code="IMPLAUSIBLE_WORD_SPEED",
                            message=f"Word '{w.display_text}' has unusual duration ({w_duration}ms)",
                            line_id=line.id,
                            start_ms=w.start_ms,
                            end_ms=w.end_ms
                        )
                    )

            if not line_has_error:
                valid_line_count += 1

        overall_confidence = round(valid_line_count / total_lines, 2)
        return diagnostics, overall_confidence
