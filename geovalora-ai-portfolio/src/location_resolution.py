"""Portfolio-safe territorial-resolution utilities for GeoValora AI.

The private application reads a prepared territorial catalog from a project
asset. This public module receives a pandas DataFrame directly, so no private
catalog or row-level housing dataset is required.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

import pandas as pd


_REQUIRED_COLUMNS = {
    "TERRITORY_ID",
    "NIVEL_SOLICITADO",
    "CIUDAD",
    "PERFIL_TECNICO_ID",
    "NIVEL_EFECTIVO",
    "CALIDAD_TERRITORIAL",
}


def normalize_text(value: Any) -> str:
    """Normalize user-entered geographical text for robust matching."""
    if value is None:
        return ""

    text = unicodedata.normalize(
        "NFKD",
        str(value).strip().lower(),
    )

    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def validate_catalog(catalog: pd.DataFrame) -> pd.DataFrame:
    """Validate the minimal territorial catalog contract."""
    if not isinstance(catalog, pd.DataFrame):
        raise TypeError("catalog must be a pandas DataFrame.")

    missing = _REQUIRED_COLUMNS - set(catalog.columns)
    if missing:
        raise ValueError(
            "Missing territorial-contract columns: "
            + ", ".join(sorted(missing))
        )

    return catalog.copy()


def _filter_text(
    dataframe: pd.DataFrame,
    column: str,
    value: Any,
) -> pd.DataFrame:
    target = normalize_text(value)

    return dataframe.loc[
        dataframe[column]
        .fillna("")
        .map(normalize_text)
        .eq(target)
    ].copy()


def list_cities(catalog: pd.DataFrame) -> list[str]:
    """List selectable cities from the catalog."""
    data = validate_catalog(catalog)

    return (
        data.loc[
            data["NIVEL_SOLICITADO"].eq("CIUDAD"),
            "CIUDAD",
        ]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def list_districts(
    catalog: pd.DataFrame,
    city: str,
) -> list[str]:
    """List districts available for one city."""
    data = validate_catalog(catalog)

    if "DISTRITO_NOMBRE" not in data.columns:
        raise ValueError("Catalog does not contain district names.")

    data = data.loc[
        data["NIVEL_SOLICITADO"].eq("DISTRITO")
    ].copy()
    data = _filter_text(data, "CIUDAD", city)

    return (
        data["DISTRITO_NOMBRE"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def list_neighborhoods(
    catalog: pd.DataFrame,
    city: str,
    district: str,
) -> list[str]:
    """List neighborhoods available for a city/district pair."""
    data = validate_catalog(catalog)

    required = {"DISTRITO_NOMBRE", "BARRIO_NOMBRE"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(
            "Catalog does not contain neighborhood hierarchy columns."
        )

    data = data.loc[
        data["NIVEL_SOLICITADO"].eq("BARRIO")
    ].copy()
    data = _filter_text(data, "CIUDAD", city)
    data = _filter_text(data, "DISTRITO_NOMBRE", district)

    return (
        data["BARRIO_NOMBRE"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .tolist()
    )


def resolve_location(
    catalog: pd.DataFrame,
    *,
    city: str,
    district: str | None = None,
    neighborhood: str | None = None,
) -> dict[str, Any]:
    """Resolve a hierarchical location to exactly one territorial record.

    The output preserves the distinction between the level requested by the
    user and the effective evidence level selected by the catalog.
    """
    if neighborhood is not None and district is None:
        raise ValueError(
            "A neighborhood cannot be selected without its district."
        )

    data = validate_catalog(catalog)

    if neighborhood is not None:
        requested_level = "BARRIO"
    elif district is not None:
        requested_level = "DISTRITO"
    else:
        requested_level = "CIUDAD"

    data = data.loc[
        data["NIVEL_SOLICITADO"].eq(requested_level)
    ].copy()
    data = _filter_text(data, "CIUDAD", city)

    if district is not None:
        if "DISTRITO_NOMBRE" not in data.columns:
            raise ValueError("Catalog does not contain district names.")
        data = _filter_text(data, "DISTRITO_NOMBRE", district)

    if neighborhood is not None:
        if "BARRIO_NOMBRE" not in data.columns:
            raise ValueError("Catalog does not contain neighborhood names.")
        data = _filter_text(data, "BARRIO_NOMBRE", neighborhood)

    if len(data) != 1:
        raise ValueError(
            "Location must resolve to exactly one territorial record."
        )

    row = data.iloc[0]

    result = {
        "territory_id": row.get("TERRITORY_ID"),
        "city": row.get("CIUDAD"),
        "district": row.get("DISTRITO_NOMBRE"),
        "neighborhood": row.get("BARRIO_NOMBRE"),
        "requested_level": row.get("NIVEL_SOLICITADO"),
        "effective_level": row.get("NIVEL_EFECTIVO"),
        "technical_profile_id": row.get("PERFIL_TECNICO_ID"),
        "territorial_quality": row.get("CALIDAD_TERRITORIAL"),
        "longitude": row.get("LONGITUDE_REF"),
        "latitude": row.get("LATITUDE_REF"),
    }

    result["degradation_applied"] = (
        result["requested_level"] != result["effective_level"]
    )

    return result
