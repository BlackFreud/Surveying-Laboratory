# Digital Terrain Model (DTM) Simulator

An interactive Digital Terrain Model simulator built for the **Civil Engineering Surveying Laboratory** at the **University of Mindanao**, College of Engineering Education (CEE). Built as an interactive laboratory innovation exhibit.

The app demonstrates the full surveying-to-engineering workflow:

**Field Survey Data → Coordinate Processing → Terrain Surface Generation → Contour Mapping → Engineering Interpretation**

## Features

| Page | What it does |
|---|---|
| **Exhibit Dashboard** *(default landing page)* | Single consolidated screen for laboratory demonstrations: upload or one-click-load sample data, 2D contour map and 3D terrain side by side, and a condensed Elevation / Slope / Volume summary |
| **Presentation Mode** | One-click guided demonstration — auto-loads sample data and walks through four narrated steps (Survey Points → Terrain Surface → Contour Map → Engineering Decision) with Back/Next/Restart controls |
| **Survey Data Input** | Manual entry (editable table) or CSV upload of survey points, with validation (missing values, duplicate point IDs, invalid coordinates) and a PRS92 coordinate-zone reference note |
| **Terrain Surface Generation** | Builds a Triangulated Irregular Network (TIN) via Delaunay triangulation; shows a 2D triangulation view and an interactive 3D terrain surface |
| **Contour Generation** | Interpolates the TIN onto a regular grid and generates a filled, labeled contour map at a selectable interval (0.5 / 1.0 / 2.0 / 5.0 m) |
| **Engineering Analysis** | Elevation statistics, slope analysis classified per the Philippine **BSWM slope grouping standard** (with a PD 705 forestland-threshold note), and estimated drainage direction |
| **Scenario Simulation** | Road construction cut/fill volume estimate for a proposed level road elevation, with **DPWH** reference embankment slope ratios shown for comparison |

## Philippine standards referenced

- **PRS92** (Philippine Reference System 1992) — coordinate zone context (informational; the app does not reproject coordinates)
- **BSWM slope classification** (Bureau of Soils and Water Management) — the six-band slope grouping (A–F) used nationwide in Philippine land and geohazard evaluation, including the PD 705 18% forestland threshold
- **DPWH** (Department of Public Works and Highways) — reference minimum fill slope and cut slope ratios by material, shown for comparison alongside the simulated cut/fill volumes

These are informational/reference implementations for an educational exhibit, not a certified survey or engineering design tool.

## Tech stack

- [Streamlit](https://streamlit.io/) — UI and native multipage navigation (`st.Page` / `st.navigation`)
- [Plotly](https://plotly.com/python/) — 2D/3D interactive visualizations
- NumPy / Pandas — data handling
- SciPy — Delaunay triangulation and grid interpolation

## Project structure

```
DTM_Simulator/
├── app.py                                 # Entrypoint: page config, global CSS, branding header, navigation
├── requirements.txt
├── pages/
│   ├── 6_dashboard.py                     # Consolidated exhibit dashboard (default landing page)
│   ├── 7_presentation_mode.py             # Guided one-click demonstration mode
│   ├── 1_survey_data_input.py
│   ├── 2_terrain_surface_generation.py
│   ├── 3_contour_generation.py
│   ├── 4_engineering_analysis.py
│   └── 5_scenario_simulation.py
├── modules/
│   ├── data_processing.py                 # Load / validate / summarize survey points
│   ├── terrain_model.py                   # TIN generation (Delaunay), cached
│   ├── contour.py                         # Grid interpolation + contour levels, cached
│   ├── analysis.py                        # Elevation, slope, drainage, cut/fill; PH standard reference values
│   └── viz.py                             # Shared Plotly chart builders + design tokens
├── assets/                                # UM / CEE logos used in the branding header
└── data/
    └── survey_points.csv                  # Sample dataset (63 points; hill, ridge, and drainage valley)
```

## Running locally

```bash
git clone <your-repo-url>
cd DTM_Simulator
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501` on the **Exhibit Dashboard**. Click **Load Sample Data** to try every page immediately, or go to **Presentation Mode** for a guided walkthrough.

## Deployment

Deployed for free on [Streamlit Community Cloud](https://share.streamlit.io):

1. Push this repository to GitHub (public, or one private app on the free tier).
2. On Streamlit Community Cloud, create a new app pointing at this repo with **`app.py`** as the main file.
3. No secrets or API keys are required.

> Free-tier apps sleep after ~12 hours without traffic and take a few seconds to wake on the next visit. For live demonstrations, either open the link a few minutes beforehand or run the app locally on the exhibit machine.

## Roadmap

- [x] Phase 1 — Survey Data Input
- [x] Phase 2 — Terrain Surface Generation
- [x] Phase 3 — Contour Generation
- [x] Phase 4 — Engineering Analysis
- [x] Phase 5 — Scenario Simulation (Road Construction)
- [x] Phase 6 — Consolidated exhibit dashboard
- [x] Phase 7 — One-click presentation / demonstration mode
- [ ] Phase 8 — User manual, lab activity sheet, evidence folder

## Credits

**Developed by Engr. JF Item**
Laboratory Custodian, Surveying Laboratory

**University of Mindanao** — Civil Engineering Laboratory
College of Engineering Education (CEE)