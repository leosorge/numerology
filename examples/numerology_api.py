
"""Example Flask API for numerology analysis modes.

This module is a drop-in reference for a numerology service where clients can:
- run only text analysis
- run only birth-number analysis (string/number, no date validation)
- run both analyses in one request
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from flask import Flask, jsonify, request

VOWELS = set("AEIOU")


@dataclass
class NumerologyResult:
    output_cons: Optional[int] = None
    output_vocs: Optional[int] = None
    output_tots: Optional[int] = None
    output_data: Optional[int] = None

    def as_dict(self) -> Dict[str, Optional[int]]:
        return {
            "output_cons": self.output_cons,
            "output_vocs": self.output_vocs,
            "output_tots": self.output_tots,
            "output_data": self.output_data,
        }


def digital_root(value: int) -> int:
    while value > 9:
        value = sum(int(digit) for digit in str(value))
    return value


def analyze_text(name: str, surname: str) -> Dict[str, int]:
    full_name = f"{name}{surname}".upper()

    cons_sum = sum((ord(ch) - 64) for ch in full_name if ch.isalpha() and ch not in VOWELS)
    vocs_sum = sum((ord(ch) - 64) for ch in full_name if ch.isalpha() and ch in VOWELS)

    output_cons = digital_root(cons_sum)
    output_vocs = digital_root(vocs_sum)
    output_tots = digital_root(output_cons + output_vocs)

    return {
        "output_cons": output_cons,
        "output_vocs": output_vocs,
        "output_tots": output_tots,
    }


def analyze_birth_number(birth_number: str) -> Dict[str, int]:
    digits_sum = sum(int(ch) for ch in birth_number if ch.isdigit())
    return {"output_data": digital_root(digits_sum)}


def validate_mode(mode: str) -> bool:
    return mode in {"text", "date", "both"}


app = Flask(__name__)


@app.post("/api/numerology")
def numerology() -> tuple:
    payload = request.get_json(silent=True) or {}

    mode = str(payload.get("mode", "both")).lower().strip()
    if not validate_mode(mode):
        return jsonify({"error": "Invalid mode. Use: text, date, both."}), 400

    name = str(payload.get("name", "")).strip()
    surname = str(payload.get("surname", "")).strip()
    birth_number = str(payload.get("birth_number", "")).strip()

    result = NumerologyResult()

    if mode in {"text", "both"}:
        if not name or not surname:
            return jsonify({"error": "name and surname are required for text mode."}), 400
        text_result = analyze_text(name, surname)
        result.output_cons = text_result["output_cons"]
        result.output_vocs = text_result["output_vocs"]
        result.output_tots = text_result["output_tots"]

    if mode in {"date", "both"}:
        if not birth_number:
            return jsonify({"error": "birth_number is required for date mode."}), 400
        date_result = analyze_birth_number(birth_number)
        result.output_data = date_result["output_data"]

    return jsonify({"mode": mode, **result.as_dict()})

# QUESTE RIGHE DEVONO ESSERE CONTRO IL MARGINE SINISTRO
if __name__ == "__main__":
    app.run(debug=True)
