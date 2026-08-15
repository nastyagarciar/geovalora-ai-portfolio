"""Portfolio-safe runtime orchestration utilities for GeoValora AI.

This module is derived from the private application runtime but deliberately
uses dependency injection instead of importing private model, territorial or
temporal assets.

It demonstrates:
- defensive extraction of prediction payloads;
- interval validation;
- optional comparison with an announced price;
- construction and validation of a shared application state.
"""

from __future__ import annotations

from datetime import datetime
import math
from typing import Any, Callable, Mapping


def _numeric_value(value: Any) -> float | None:
    """Return a finite float or None."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    return number if math.isfinite(number) else None


def _first_numeric(
    data: Mapping[str, Any],
    paths: list[tuple[str, ...]],
) -> float | None:
    """Return the first finite numeric value found in a nested mapping."""
    for path in paths:
        current: Any = data

        for key in path:
            if not isinstance(current, Mapping) or key not in current:
                break
            current = current[key]
        else:
            value = _numeric_value(current)
            if value is not None:
                return value

    return None


def extract_prediction(base_result: Mapping[str, Any]) -> float:
    """Extract a positive prediction from a model-result payload."""
    if not isinstance(base_result, Mapping):
        raise TypeError("base_result must be a mapping.")

    prediction = _first_numeric(
        base_result,
        [
            ("prediction", "price_eur"),
            ("prediction", "prediction_price"),
            ("prediction_price_eur",),
            ("prediction_eur",),
            ("prediccion_eur",),
            ("valor_estimado",),
        ],
    )

    if prediction is None:
        raise KeyError("No numeric prediction was found in base_result.")

    if prediction <= 0:
        raise ValueError("The base prediction must be positive.")

    return prediction


def extract_interval(
    base_result: Mapping[str, Any],
) -> tuple[float | None, float | None]:
    """Extract and validate an optional prediction interval."""
    lower = _first_numeric(
        base_result,
        [
            ("interval", "lower_price"),
            ("interval", "lower"),
            ("interval_lower_eur",),
            ("interval_lower",),
            ("lower",),
        ],
    )

    upper = _first_numeric(
        base_result,
        [
            ("interval", "upper_price"),
            ("interval", "upper"),
            ("interval_upper_eur",),
            ("interval_upper",),
            ("upper",),
        ],
    )

    if lower is None and upper is None:
        return None, None

    if lower is None or upper is None:
        raise ValueError("Both interval limits must be provided together.")

    if lower <= 0 or upper <= lower:
        raise ValueError("The prediction interval is invalid.")

    return lower, upper


def compare_announced_price(
    announced_price: float | None,
    prediction: float,
    lower: float | None = None,
    upper: float | None = None,
) -> dict[str, Any] | None:
    """Compare an optional announced price with the model estimate.

    The classification is descriptive only; it is not a buy/sell signal.
    """
    if announced_price is None:
        return None

    announced = float(announced_price)

    if not math.isfinite(announced) or announced <= 0:
        raise ValueError("The announced price must be positive and finite.")

    difference = announced - prediction
    difference_pct = difference / prediction * 100

    if lower is not None and upper is not None:
        if announced < lower:
            classification = "BELOW_INTERVAL"
        elif announced > upper:
            classification = "ABOVE_INTERVAL"
        else:
            classification = "WITHIN_INTERVAL"
    else:
        classification = "NO_INTERVAL"

    return {
        "announced_price_eur": announced,
        "difference_eur": difference,
        "difference_pct": difference_pct,
        "classification": classification,
        "warning": (
            "This comparison is descriptive and does not constitute "
            "a purchase, sale or investment recommendation."
        ),
    }


def build_app_state(
    *,
    property_input: Mapping[str, Any],
    base_result: Mapping[str, Any],
    city: str,
    location_resolver: Callable[..., Mapping[str, Any]],
    temporal_contextualizer: Callable[..., Mapping[str, Any]] | None = None,
    district: str | None = None,
    neighborhood: str | None = None,
    announced_price: float | None = None,
) -> dict[str, Any]:
    """Build a single state object consumed by downstream UI/reporting layers.

    External dependencies are passed as callables so this public portfolio
    module does not depend on private datasets or serialized model artifacts.
    """
    location = location_resolver(
        city=city,
        district=district,
        neighborhood=neighborhood,
    )

    prediction = extract_prediction(base_result)
    lower, upper = extract_interval(base_result)

    temporal_result = None
    if temporal_contextualizer is not None:
        temporal_result = temporal_contextualizer(
            city=city,
            historical_prediction=prediction,
            historical_lower=lower,
            historical_upper=upper,
        )

    state = {
        "input": dict(property_input),
        "location": dict(location),
        "base_result": dict(base_result),
        "temporal_context": temporal_result,
        "comparison": compare_announced_price(
            announced_price=announced_price,
            prediction=prediction,
            lower=lower,
            upper=upper,
        ),
        "metadata": {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "state_version": "portfolio-1.0",
            "historical_prediction": prediction,
            "historical_interval_lower": lower,
            "historical_interval_upper": upper,
        },
    }

    validate_app_state(state)
    return state


def validate_app_state(state: Mapping[str, Any]) -> bool:
    """Validate the minimal contract for the shared application state."""
    required = {
        "input",
        "location",
        "base_result",
        "temporal_context",
        "comparison",
        "metadata",
    }

    missing = required - set(state)
    if missing:
        raise ValueError(
            "Incomplete application state: " + ", ".join(sorted(missing))
        )

    if not isinstance(state["location"], Mapping):
        raise TypeError("state['location'] must be a mapping.")

    return True
