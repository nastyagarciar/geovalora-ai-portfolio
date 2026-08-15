# Selected GeoValora AI Source Code

This folder contains a small, sanitized subset of the application architecture
published for portfolio review.

## Files

- `runtime_state.py` — defensive parsing, interval validation and shared-state orchestration.
- `temporal_context.py` — externally supplied temporal contextualization with safeguards against double application.
- `location_resolution.py` — hierarchical city/district/neighborhood resolution from a supplied catalog.

## Public portfolio boundary

These modules intentionally do **not** include:

- the original or processed housing datasets;
- serialized XGBoost or SHAP artifacts;
- private territorial catalogs;
- row-level TEST predictions;
- Google Drive paths;
- internal release or backup files.

External data and application assets are injected into the public examples rather
than bundled with the portfolio.
