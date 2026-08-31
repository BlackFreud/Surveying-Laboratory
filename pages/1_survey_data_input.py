"""
pages/1_survey_data_input.py

Survey Data Input page — manual entry or CSV upload of survey points,
with validation and a PRS92 coordinate reference note.
"""

import pandas as pd
import streamlit as st

from modules.data_processing import (
    load_manual_points,
    load_csv_points,
    validate_points,
    summarize_points,
)
from modules.analysis import PRS92_ZONES

st.subheader("Survey Data Input")
st.caption("Enter survey points manually or upload a CSV file.")

with st.expander("Coordinate reference (PRS92)", expanded=False):
    zone_name = st.selectbox(
        "Survey Zone",
        options=list(PRS92_ZONES.keys()),
        index=2,  # Zone III (Luzon, Manila) as a common default
        key="prs92_zone",
        help="Informational only — coordinates below are used as entered "
             "(local project grid) and are not reprojected.",
    )
    st.caption(
        f"Central meridian: {PRS92_ZONES[zone_name]}°E &nbsp;·&nbsp; "
        f"Philippine Reference System 1992 (PRS92), Clarke 1866 ellipsoid.",
        unsafe_allow_html=True,
    )

input_method = st.radio(
    "Input method", ["Manual Input", "CSV Upload"], horizontal=True, key="input_method"
)

raw_df = None
csv_error = None

if input_method == "Manual Input":
    with st.form("manual_input_form"):
        st.write("Edit the table below, then click **Load Points**.")
        starter_df = pd.DataFrame(
            {
                "Point": ["P1", "P2"],
                "Easting": [100.0, 110.0],
                "Northing": [100.0, 100.0],
                "Elevation": [52.30, 53.10],
            }
        )
        edited_df = st.data_editor(
            starter_df,
            num_rows="dynamic",
            width="stretch",
            key="manual_points_editor",
            column_config={
                "Point": st.column_config.TextColumn("Point"),
                "Easting": st.column_config.NumberColumn("Easting", format="%.2f"),
                "Northing": st.column_config.NumberColumn("Northing", format="%.2f"),
                "Elevation": st.column_config.NumberColumn("Elevation", format="%.2f"),
            },
        )
        submitted = st.form_submit_button("Load Points", type="primary")

    if submitted:
        raw_df = load_manual_points(edited_df)
        st.session_state["manual_raw_df"] = raw_df
    elif "manual_raw_df" in st.session_state:
        # Reuse the last submitted table on reruns that aren't a fresh
        # submit (e.g. switching to the CSV tab and back), so the loaded
        # data doesn't silently disappear.
        raw_df = st.session_state["manual_raw_df"]

else:  # CSV Upload
    st.write("CSV must have columns: `Point, Easting, Northing, Elevation`")
    uploaded_file = st.file_uploader(
        "Upload survey_points.csv", type=["csv"], key="csv_uploader"
    )
    if uploaded_file is not None:
        raw_df, csv_error = load_csv_points(uploaded_file)

st.divider()

if csv_error:
    st.error(csv_error)
elif raw_df is not None and not raw_df.empty:
    issues = validate_points(raw_df)

    if issues:
        st.warning("Validation issues found:")
        for issue in issues:
            st.markdown(f"- {issue}")
        st.info("Fix the issues above to proceed. The data below is shown as-entered.")
        st.dataframe(raw_df, width="stretch")
    else:
        summary = summarize_points(raw_df)
        st.success("Survey points loaded and validated successfully.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Survey Points", f"{summary['total_points']} loaded")
        col2.metric("Minimum Elevation", f"{summary['min_elevation']:.2f} m")
        col3.metric("Maximum Elevation", f"{summary['max_elevation']:.2f} m")

        st.dataframe(raw_df, width="stretch")

        # Store validated points for later pages (terrain generation, etc.)
        st.session_state["survey_points"] = raw_df
elif "survey_points" in st.session_state:
    # Nothing fresh was submitted/uploaded this run (e.g. the person
    # switched input-method tabs — Streamlit forgets a widget's state when
    # it isn't rendered on a given run). The previously loaded/validated
    # dataset is still valid, so keep showing it instead of treating this
    # as "nothing loaded."
    existing_df = st.session_state["survey_points"]
    summary = summarize_points(existing_df)
    st.success("Survey points loaded and validated successfully.")
    st.caption("Showing previously loaded data for this session.")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Survey Points", f"{summary['total_points']} loaded")
    col2.metric("Minimum Elevation", f"{summary['min_elevation']:.2f} m")
    col3.metric("Maximum Elevation", f"{summary['max_elevation']:.2f} m")

    st.dataframe(existing_df, width="stretch")
else:
    st.info("No survey points loaded yet.")