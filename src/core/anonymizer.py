"""KUERA AI — Data Anonymizer for Cloud API Calls.

Strips PII and sensitive institutional identifiers before sending
data to external (cloud) model APIs.

Usage:
    from src.core.anonymizer import Anonymizer
    anon = Anonymizer()
    clean_text = anon.sanitize(text_with_pii)
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class AnonymizationResult:
    text: str
    replacements: Dict[str, str]
    risk_score: int  # 0-100, higher = more sensitive data found


class Anonymizer:
    """PII and sensitive data anonymizer for audit context."""

    # Patterns that indicate sensitive data
    PATTERNS = {
        # Personal identifiers
        "nip": re.compile(r"\b\d{18}\b"),  # 18-digit Indonesian NIP
        "nik": re.compile(r"\b\d{16}\b"),  # 16-digit Indonesian NIK
        "npwp": re.compile(r"\b\d{2}\.\d{3}\.\d{3}\.\d{1}-\d{3}\.\d{3}\b"),
        "phone": re.compile(r"\b(?:\+62|0)\d{9,12}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),

        # Institutional patterns
        "nomor_surat": re.compile(r"\b[A-Z]{2}\.\d{2}\.\d{2}/[A-Z]+-\d+/[A-Z]+\d+/\d{4}\b"),
        "kode_wilayah": re.compile(r"\b\d{2}\.\d{2}\.\d{2}\.\d{4}\b"),  # BPS kode wilayah

        # Financial identifiers
        "rekening": re.compile(r"\b\d{10,16}\b"),  # Bank account (heuristic)
    }

    # Entity name patterns (heuristic — long capitalized phrases)
    ENTITY_PATTERN = re.compile(r"\b(?:PDAM|Perumdam|Perusahaan|BUMD|BUMDes|Dinas|Badan|Kantor|PT|CV)\s+[A-Za-z\s]{3,50}")

    def __init__(self):
        self._counter = 0
        self._replacements: Dict[str, str] = {}

    def _next_token(self, category: str) -> str:
        self._counter += 1
        return f"[{category}_{self._counter}]"

    def _replace(self, text: str, pattern: re.Pattern, category: str) -> str:
        def replacer(match):
            original = match.group(0)
            if original in self._replacements:
                return self._replacements[original]
            token = self._next_token(category)
            self._replacements[original] = token
            return token
        return pattern.sub(replacer, text)

    def sanitize(self, text: str, anonymize_entities: bool = True) -> AnonymizationResult:
        """Sanitize text by replacing sensitive data with tokens.

        Args:
            text: Original text that may contain PII
            anonymize_entities: Also replace organization names

        Returns:
            AnonymizationResult with clean text and mapping
        """
        self._replacements = {}
        self._counter = 0
        clean = text
        risk_score = 0

        for category, pattern in self.PATTERNS.items():
            matches = list(pattern.finditer(clean))
            if matches:
                risk_score += len(matches) * 10
                clean = self._replace(clean, pattern, category.upper())

        if anonymize_entities:
            entity_matches = list(self.ENTITY_PATTERN.finditer(clean))
            if entity_matches:
                risk_score += len(entity_matches) * 5
                clean = self._replace(clean, self.ENTITY_PATTERN, "ENTITY")

        return AnonymizationResult(
            text=clean,
            replacements=self._replacements,
            risk_score=min(risk_score, 100),
        )

    def sanitize_dict(self, data: Dict, anonymize_entities: bool = True) -> AnonymizationResult:
        """Sanitize all string values in a dictionary."""
        text = json.dumps(data, ensure_ascii=False, indent=2)
        return self.sanitize(text, anonymize_entities)

    def restore(self, text: str) -> str:
        """Restore original values from tokens (best-effort)."""
        restored = text
        for original, token in self._replacements.items():
            restored = restored.replace(token, original)
        return restored


def quick_sanitize(text: str) -> str:
    """One-shot sanitize without tracking replacements."""
    anon = Anonymizer()
    return anon.sanitize(text).text
