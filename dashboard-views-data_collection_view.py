"""Admin tools for manually entering, importing, and generating telemetry datasets."""

import pandas as pd
import streamlit as st

from services.telemetry_dataset import (
    DATASET_COLUMNS,
    DATASET_PATH,
    HOUSE_IDS,
    MANUAL_ENTRY_COLUMNS,
    append_records,
    generate_synthetic_records,
    load_dataset,
)


def render_data_collection_view(user_role="ADMIN"):
    if user_role != "ADMIN":
        st.error("Dataset collection is restricted to Administrators.")
        return

    st.title("Telemetry Dataset Collection")
    st.caption(
        "Enter or import hourly apartment-meter readings for AquaNest anomaly analysis. "
        f"Records are saved locally to `{DATASET_PATH.relative_to(DATASET_PATH.parents[1])}`."
    )

    manual_tab, upload_tab, generate_tab = st.tabs(
        ["Manual Entry", "Import CSV", "Generate Sample Data"]
    )

    with manual_tab:
        st.markdown("Add one or more readings in the editable table, then save them to the project dataset.")
        st.caption(
            "Required fields: timestamp, house_id (H101–H120), litres, "
            "rolling_mean_24h, continuous_night_hours (0–6)."
        )
        empty_table = pd.DataFrame({
            "timestamp": pd.Series(dtype="str"),
            "house_id": pd.Series(dtype="str"),
            "litres": pd.Series(dtype="float"),
            "rolling_mean_24h": pd.Series(dtype="float"),
            "continuous_night_hours": pd.Series(dtype="int"),
        })
        manual_rows = st.data_editor(
            empty_table,
            num_rows="dynamic",
            use_container_width=True,
            key="manual_telemetry_editor",
            column_config={
                "house_id": st.column_config.SelectboxColumn(
                    "Apartment", options=HOUSE_IDS, required=True
                ),
                "litres": st.column_config.NumberColumn(
                    "Hourly use (L)", min_value=0.0, step=0.1, required=True
                ),
                "rolling_mean_24h": st.column_config.NumberColumn(
                    "24-hour average (L)", min_value=0.0, step=0.1, required=True
                ),
                "continuous_night_hours": st.column_config.NumberColumn(
                    "Continuous night hours", min_value=0, max_value=6, step=1, required=True
                ),
            },
        )
        if st.button("Save Manual Records", type="primary", key="save_manual_dataset"):
            try:
                added_count, _ = append_records(manual_rows, source="manual")
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(f"Saved {added_count} manual telemetry record(s).")
                st.rerun()

    with upload_tab:
        st.markdown("Import a CSV containing the same five input fields used by Manual Entry.")
        st.download_button(
            "Download CSV Template",
            data=(",".join(MANUAL_ENTRY_COLUMNS) + "\n").encode("utf-8-sig"),
            file_name="aquanest_telemetry_template.csv",
            mime="text/csv",
        )
        uploaded_file = st.file_uploader(
            "Choose telemetry CSV",
            type=["csv"],
            key="telemetry_csv_upload",
        )
        if uploaded_file is not None:
            try:
                uploaded_data = pd.read_csv(uploaded_file)
            except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
                st.error(f"Could not read the uploaded CSV: {error}")
            else:
                st.dataframe(uploaded_data.head(10), use_container_width=True)
                if st.button("Import CSV Records", type="primary", key="import_telemetry_csv"):
                    try:
                        added_count, _ = append_records(uploaded_data, source="uploaded")
                    except ValueError as error:
                        st.error(str(error))
                    else:
                        st.success(f"Imported {added_count} telemetry record(s).")
                        st.rerun()

    with generate_tab:
        st.markdown(
            f"Create project-shaped hourly readings for all {len(HOUSE_IDS)} apartments. "
            "The sample includes morning/evening demand peaks and periodic leak/burst patterns."
        )
        days = st.selectbox("Sample period", [7, 30, 90], index=1, format_func=lambda value: f"{value} days")
        if st.button("Generate and Save Sample Data", type="primary", key="generate_telemetry_dataset"):
            generated_data = generate_synthetic_records(days=days)
            added_count, _ = append_records(generated_data, source="synthetic")
            st.success(f"Generated and saved {added_count:,} synthetic telemetry record(s).")
            st.rerun()

    st.divider()
    try:
        saved_data = load_dataset()
    except (OSError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
        st.error(f"Could not read the saved telemetry dataset: {error}")
        return

    st.subheader("Saved Dataset")
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Total records", f"{len(saved_data):,}")
    metric_col2.metric("Apartments represented", saved_data["house_id"].nunique() if not saved_data.empty else 0)
    if saved_data.empty:
        st.info("No records saved yet. Add a row, import a CSV, or generate sample data.")
    else:
        st.dataframe(saved_data.tail(100), use_container_width=True, hide_index=True)
        st.download_button(
            "Download Full Dataset CSV",
            data=saved_data.loc[:, DATASET_COLUMNS].to_csv(index=False).encode("utf-8-sig"),
            file_name=DATASET_PATH.name,
            mime="text/csv",
            key="download_telemetry_dataset",
        )
