import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from views import water_consumption_view


class _Column:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class WaterConsumptionViewTests(unittest.TestCase):
    def test_empty_house_list_does_not_break_comparison_chart(self):
        api_client = Mock()
        api_client.get_houses.return_value = []
        api_client.get_consumption_summary.return_value = {}
        api_client.get_consumption_time_series.return_value = [
            {"label": "Today", "timestamp": "2026-11-19", "litres": 100}
        ]

        streamlit = Mock()
        streamlit.session_state = {"dark_theme": True}
        streamlit.columns.side_effect = lambda count: [_Column() for _ in range(
            count if isinstance(count, int) else len(count)
        )]
        streamlit.selectbox.return_value = "ALL (Entire Apartment)"

        with patch.object(water_consumption_view, "st", streamlit), patch.object(
            water_consumption_view, "chart_hourly_profile", return_value=Mock()
        ), patch.object(
            water_consumption_view, "chart_daily_consumption", return_value=Mock()
        ), patch.object(
            water_consumption_view, "format_plotly_chart", return_value=Mock()
        ), patch.object(
            water_consumption_view, "create_html_csv_download_button", return_value=""
        ):
            water_consumption_view.render_water_consumption(api_client)

        streamlit.info.assert_called_once_with(
            "No apartment usage data is currently available for comparison."
        )
        self.assertEqual(streamlit.plotly_chart.call_count, 5)


if __name__ == "__main__":
    unittest.main()
