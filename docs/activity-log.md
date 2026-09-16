# Activity Log

## [2026-09-16] Codebase Quality, Security, and Architecture Refactoring

### Objectives
Refactor the Digital Terrain Model (DTM) Simulator following PEP8, explicit type hints, pytest best practices, FastAPI/Django architectural conventions (separation of concerns, typed schemas, DTOs), and Python security guidelines.

### Changes Implemented
1. **Critical & Runtime Fixes**:
   - Fixed gitignore configuration by replacing legacy middle-dot file name with `.gitignore`.
   - Prevented calculation divergence by capping infinite slope at vertical faces to a finite boundary (`999.9%`).
   - Hardened `pages/7_presentation_mode.py` demo start routine against data loading failures and duplicate state.
   - Pinned dependencies in `requirements.txt` to stable releases with upper bounds.
   - Promoted `sample_4_um_matina_campus.csv` (625 survey points) into the sample registry and cleaned up duplicate/untracked legacy CSV files.

2. **Security & Input Guardrails**:
   - Configured `.streamlit/config.toml` to enforce a 5 MB maximum upload size limit.
   - Added a `10,000` row-count safeguard (`MAX_SURVEY_POINTS`) in `modules/data_processing.py` to prevent memory exhaustion and DoS from oversized CSV uploads.
   - Replaced blind exception handling (`except Exception`) with specific expected exceptions (`ParserError`, `EmptyDataError`, `UnicodeDecodeError`, `ValueError`, `OSError`, `QhullError`).
   - Audited all occurrences of `unsafe_allow_html=True` across the application to ensure only server-controlled markup is rendered with zero unescaped user inputs.

3. **Performance Optimization**:
   - Optimized `modules/viz.py` `build_cutfill_figure` from $O(N)$ individual Plotly traces to exactly 2 vectorized traces (`cut` and `fill`) using `None`-separated polygon paths.

4. **Typing & FastAPI/Django Architectural Conventions**:
   - Introduced strong typing with explicit schemas and TypedDict definitions:
     - `PointSummary` (`modules/data_processing.py`)
     - `SurfaceMesh` (`modules/terrain_model.py`)
     - `ContourGrid` (`modules/contour.py`)
     - `ElevationStats`, `SlopeClassification`, `SlopeStats`, `DrainageResult`, `CutFillTriangle`, `RoadSimResult` (`modules/analysis.py`)
     - `SampleDataset` (`modules/samples.py`)
   - Decoupled UI presentation into a reusable component `modules/components.py` (`render_engineering_summary`), eliminating repeated markup across `6_dashboard.py`, `7_presentation_mode.py`, and `4_engineering_analysis.py`.
   - Consolidated design tokens (`MAROON`, `GOLD`, `MUTED`, `MUTED_LIGHT`, `BORDER`, `DISABLED`) in `modules/viz.py` and eliminated magic color strings across views.

5. **Pytest Test Suite**:
   - Configured `pyproject.toml` with pytest, ruff, and mypy settings.
   - Implemented 65 unit and integration tests across 6 test modules in `tests/`:
     - `tests/test_data_processing.py`
     - `tests/test_terrain_model.py`
     - `tests/test_analysis.py`
     - `tests/test_contour.py`
     - `tests/test_components.py`
     - `tests/test_viz.py`
     - `tests/test_samples.py`
   - Verified 100% test pass rate, 0 ruff lint errors, and 0 mypy type errors.
