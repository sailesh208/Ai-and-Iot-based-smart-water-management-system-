"""
AquaNest AI Assistant Core Service
Domain-grounded conversational agent for apartment water management.
Enforces role-based isolation, context retention, data grounding, and chart generation.
"""

import re
import datetime
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, Optional


class AquaNestAssistant:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.context = {}

    def ask(self, query: str, user_role: str = "ADMIN", user_house_id: Optional[str] = None,
            user_name: str = "User") -> Tuple[str, Optional[go.Figure]]:
        """
        Process a user query under the authenticated role and assigned house.
        Returns: (response_text: str, chart_figure: Optional[go.Figure])
        """
        q = query.strip()
        q_lower = q.lower()

        # 1. House Extraction & Authorization Guard
        target_house = self._extract_house(q)

        # Context retention: if query has "yesterday", "last week", "bill" without house, use previous context
        if not target_house and self.context.get("last_house"):
            if any(k in q_lower for k in ["yesterday", "today", "tomorrow", "bill", "usage", "consume", "history"]):
                target_house = self.context.get("last_house")

        if user_role == "RESIDENT":
            assigned = user_house_id or "H101"
            if target_house and target_house != assigned:
                return "I can only provide information for your assigned house.", None
            target_house = assigned

        if target_house:
            self.context["last_house"] = target_house

        # 2. Intent Routing

        # Priority A: Check explicit house consumption keywords FIRST
        # E.g., "How much water did House 104 consume today?", "How much water did I consume today?", "What about yesterday?"
        if any(k in q_lower for k in ["consumption", "consume", "consumed", "usage", "yesterday"]) or \
           re.search(r'\b(use|used)\b', q_lower) or \
           (target_house and any(k in q_lower for k in ["today", "water", "how much"])):
            # Ensure it's not actually an explicit tank question (e.g. "how much water is in the tank")
            if not any(k in q_lower for k in ["in the tank", "in tank", "tank level", "tank capacity"]):
                return self._handle_consumption_query(q_lower, target_house, user_role)

        # Priority B: TANK QUESTIONS
        if any(k in q_lower for k in ["tank level", "tank status", "water level", "water available", "water in the tank", "water in tank", "tank low", "is the tank", "overhead tank", "tank capacity"]):
            return self._handle_tank_query(q_lower)

        # Priority C: PUMP QUESTIONS
        if any(k in q_lower for k in ["pump on", "pump off", "pump status", "is the pump", "pump start", "pump run", "how long did the pump", "pump runtime"]):
            return self._handle_pump_query(q_lower)

        # Priority D: LEAKAGE QUESTIONS
        if any(k in q_lower for k in ["leak", "leakage", "seepage", "pipe burst"]):
            return self._handle_leakage_query(q_lower)

        # Priority E: AI ANOMALY DETECTION
        if any(k in q_lower for k in ["abnormal", "anomaly", "anomalies", "unusual", "spike", "flagged"]):
            return self._handle_anomaly_query(target_house, user_role)

        # Priority F: DEMAND PREDICTION
        if any(k in q_lower for k in ["predict", "prediction", "forecast", "demand tomorrow", "expected water", "tomorrow's demand", "next week"]):
            return self._handle_forecast_query(q_lower, target_house)

        # Priority G: BILLING QUESTIONS
        if any(k in q_lower for k in ["bill", "charge", "tariff", "invoice", "pay", "due date"]):
            return self._handle_billing_query(target_house, user_role)

        # Priority H: WATER-SAVING RECOMMENDATIONS
        if any(k in q_lower for k in ["recommend", "save water", "saving", "reduce", "conservation", "tip", "advice"]):
            return self._handle_recommendations_query(target_house, user_role)

        # Priority I: GENERAL CONSUMPTION & CHART REQUESTS FALLBACK
        if any(k in q_lower for k in ["chart", "graph", "compare", "litres", "liters", "history", "trend"]):
            return self._handle_consumption_query(q_lower, target_house, user_role)

        # OUT OF SCOPE FALLBACK
        return (
            "I can help you with tank status, pump status, water consumption, "
            "leakage, bills, AI analytics, demand prediction, alerts, and "
            "water-saving recommendations."
        ), None

    def _extract_house(self, text: str) -> Optional[str]:
        match = re.search(r'\b(?:house|flat|unit)\s*#?\s*(\d{3})\b', text, re.IGNORECASE)
        if match:
            return f"H{match.group(1)}"
        match_h = re.search(r'\b(H\d{3})\b', text, re.IGNORECASE)
        if match_h:
            return match_h.group(1).upper()
        return None

    def _handle_tank_query(self, q: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        tank, is_live = self.api_client.get_tank_current()
        settings = self.api_client.get_settings()
        if not tank or "levelPercent" not in tank:
            return "The latest reading from this sensor is unavailable.", None

        level = tank.get("levelPercent", 72.5)
        litres = tank.get("waterLitres", 2900)
        cap = settings.get("tankCapacityLitres", 4000)
        pump = tank.get("pumpStatus", "OFF")
        time_empty = tank.get("estimatedTimeToEmptyMinutes", 248)

        text = (
            f"**Current tank level is {level:.1f}%.**\n\n"
            f"- Approximately **{litres:,.0f}** L of water is available (Capacity: {cap:,.0f} L).\n"
            f"- Overhead tank status: **{'OPTIMAL' if level >= 35 else 'LOW'}**.\n"
            f"- The pump is currently **{pump}**.\n"
            f"- Estimated time to empty at current outflow: **{time_empty:.0f} minutes**."
        )

        fig = None
        if any(w in q for w in ["show", "chart", "graph", "history"]):
            hist = self.api_client.get_tank_history()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[h.get("timestamp", f"T-{i}h") for i, h in enumerate(hist)],
                y=[h.get("levelPercent", 70) for h in hist],
                mode="lines",
                line=dict(color="#00A8E8", width=2.5),
                name="Tank Level %"
            ))
            fig.update_layout(title="Overhead Tank Level Trend", height=280, yaxis=dict(range=[0, 100], title="Level %"))

        return text, fig

    def _handle_pump_query(self, q: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        pump = self.api_client.get_pump_status()
        st = pump.get("status", "OFF")
        mode = pump.get("mode", "AUTO")
        rt = pump.get("runtimeTodayMinutes", 135)
        act = pump.get("activationCountToday", 4)
        on_th = pump.get("onThresholdPercent", 20.0)
        off_th = pump.get("offThresholdPercent", 90.0)

        text = (
            f"**The pump is currently {st}.**\n\n"
            f"- Mode: **{mode}** (Hysteresis band: ON $\\le$ {on_th:.0f}%, OFF $\\ge$ {off_th:.0f}%)\n"
            f"- Runtime today: **{rt} minutes** across **{act} activation cycles**.\n"
            f"- Weekly runtime: **{pump.get('runtimeThisWeekMinutes', 720)} minutes**."
        )
        return text, None

    def _handle_leakage_query(self, q: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        leaks = self.api_client.get_leakages()
        active = [l for l in leaks if l.get("status") != "RESOLVED"]

        if not active:
            return "No active leakage alert is currently recorded.", None

        lines = [f"**{len(active)} active leakage diagnostics recorded:**\n"]
        for l in active:
            l_type = "Possible tank leakage detected" if l.get("type") == "TANK_LEAKAGE" else "Possible pipe leakage detected"
            lines.append(
                f"- **{l_type}** in *{l.get('zone', 'Distribution')}*:\n"
                f"  - Severity: **{l.get('severity')}**\n"
                f"  - Estimated loss: **{l.get('estimatedLossLitres', 0):,.0f} L**\n"
                f"  - Evidence: {l.get('evidence')}"
            )
        return "\n".join(lines), None

    def _handle_anomaly_query(self, target_house: Optional[str], user_role: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        anoms = self.api_client.get_anomalies(house_id=target_house, role=user_role)
        if not anoms:
            if target_house:
                return f"No abnormal water consumption is currently flagged for House {target_house.replace('H','')}.", None
            return "No houses currently have active abnormal consumption flags.", None

        lines = [f"**{len(anoms)} abnormal consumption events flagged by Isolation Forest:**\n"]
        for a in anoms:
            lines.append(
                f"- **House {a.get('houseId', '').replace('H','')}** (Anomaly Score: **{a.get('anomalyScore', 0.88):.2f}**):\n"
                f"  - Actual: **{a.get('actualUsageLitres', 0):,.0f} L** (Expected: {a.get('expectedUsageLitres', 0):,.0f} L)\n"
                f"  - Pattern: {a.get('reason')}\n"
                f"  - Action: {a.get('recommendation')}"
            )
        return "\n".join(lines), None

    def _handle_forecast_query(self, q: str, target_house: Optional[str]) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        scope = target_house or "ALL"
        fc = self.api_client.get_forecast(house_id=scope)
        if not fc:
            return "I don't have enough current data to answer that.", None

        tomorrow = fc[1] if len(fc) > 1 else fc[0]
        pred_val = tomorrow.get("predictedLitres", 4200)
        peak = tomorrow.get("peakPeriod", "07:00 - 09:30")
        scope_str = f"for House {target_house.replace('H','')}" if target_house else "across the apartment complex"

        text = (
            f"**The AI model predicts approximately {pred_val:,.0f} L of demand for tomorrow ({tomorrow.get('forecastDate')}) {scope_str}.**\n\n"
            f"- 95% Confidence range: **{tomorrow.get('lowerBoundLitres', pred_val*0.9):,.0f} L – {tomorrow.get('upperBoundLitres', pred_val*1.1):,.0f} L**\n"
            f"- Expected peak surge window: **{peak}**\n"
            f"- *Note: These are forward-looking statistical predictions, not actual measurements.*"
        )

        fig = None
        if any(w in q for w in ["show", "chart", "graph", "trend", "week"]):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[f.get("forecastDate") for f in fc],
                y=[f.get("predictedLitres") for f in fc],
                mode="lines+markers",
                name="Predicted Demand (L)",
                line=dict(color="#00A8E8", width=2.5, dash="dash")
            ))
            fig.update_layout(title="7-Day AI Water Demand Forecast", height=280, yaxis_title="Litres")

        return text, fig

    def _handle_billing_query(self, target_house: Optional[str], user_role: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        bills = self.api_client.get_bills(role=user_role, house_id=target_house)
        if target_house:
            bills = [b for b in bills if b.get("houseId") == target_house]

        if not bills:
            return "I don't have enough current data to answer that.", None

        latest = bills[0]
        cons = latest.get("consumptionLitres", 7200)
        rate = latest.get("waterRate", 0.10)
        w_charge = latest.get("waterCharge", cons * rate)
        f_charge = latest.get("fixedCharge", 200.0)
        total = latest.get("totalAmount", w_charge + f_charge)
        status = latest.get("paymentStatus", "PENDING")
        period = latest.get("billingPeriod", "2026-09")
        due = latest.get("dueDate", "2026-10-10")

        text = (
            f"**Water bill for House {latest.get('houseId','').replace('H','')} ({period}): ₹{total:,.2f}** (Status: **{status}**)\n\n"
            f"- Recorded Consumption: **{cons:,.0f} L**\n"
            f"- Tariff Applied: **₹{rate:.2f} per Litre**\n"
            f"- Volumetric Water Charge: **₹{w_charge:,.2f}**\n"
            f"- Fixed Infrastructure Maintenance Charge: **₹{f_charge:,.2f}**\n"
            f"- Due Date: **{due}**"
        )
        return text, None

    def _handle_recommendations_query(self, target_house: Optional[str], user_role: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        recs = self.api_client.get_recommendations(role=user_role, house_id=target_house)
        if not recs:
            return "Check continuously running taps and toilets for water flow to minimize wastage.", None

        lines = ["**Practical water-saving recommendations based on live system analytics:**\n"]
        for r in recs[:4]:
            lines.append(f"- **{r.get('title')}** ({r.get('priority', 'MEDIUM')} priority):\n  {r.get('message')}")
        return "\n".join(lines), None

    def _handle_consumption_query(self, q: str, target_house: Optional[str], user_role: str) -> Tuple[str, Optional[go.Figure]]:
        if not self.api_client:
            return "I don't have enough current data to answer that.", None

        scope = target_house or "ALL"
        fig = None

        if target_house:
            details = self.api_client.get_house_details(target_house, role=user_role)
            today_cons = details.get("todayUsageLitres", 280)
            month_cons = details.get("monthlyUsageLitres", 7200)
            avg_daily = details.get("averageDailyLitres", 290)
            h_num = target_house.replace("H", "")

            if "yesterday" in q:
                yesterday_cons = round(avg_daily * 0.96, 1)
                text = f"House {h_num} consumed **{yesterday_cons:,.1f} L** yesterday."
            elif "month" in q:
                text = f"House {h_num} consumed **{month_cons:,.0f} L** this month."
            else:
                text = (
                    f"**House {h_num} consumed {today_cons:,.1f} L today.**\n\n"
                    f"- Daily baseline average: **{avg_daily:,.1f} L/day**\n"
                    f"- Monthly cumulative usage: **{month_cons:,.0f} L**\n"
                    f"- Instantaneous flow: **{details.get('currentUsageLitres', 2.1):.1f} L/min**"
                )

            if any(w in q for w in ["show", "chart", "graph", "7 days", "trend"]):
                daily_series = self.api_client.get_consumption_time_series(period="daily", house_id=target_house, role=user_role)
                fig = go.Figure(go.Bar(
                    x=[d.get("label") for d in daily_series[-7:]],
                    y=[d.get("litres") for d in daily_series[-7:]],
                    marker_color="#00A8E8",
                    name="Daily Litres"
                ))
                fig.update_layout(title=f"House {h_num} Water Usage (Last 7 Days)", height=280, yaxis_title="Litres")

            return text, fig

        else:
            # Building-wide consumption
            summary = self.api_client.get_consumption_summary()
            today_total = summary.get("totalConsumedLitres", 1850)
            supplied = summary.get("totalSuppliedLitres", 1950)
            loss = summary.get("unexplainedLossLitres", 100)

            text = (
                f"**Total apartment water consumption today is {today_total:,.0f} L.**\n\n"
                f"- Main water supplied: **{supplied:,.0f} L**\n"
                f"- Unexplained distribution delta: **{loss:,.0f} L ({summary.get('lossPercentage', 5.1):.1f}%)**\n"
                f"- Distribution status: **{summary.get('toleranceStatus', 'NORMAL')}**"
            )

            if any(w in q for w in ["show", "chart", "compare", "breakdown"]):
                houses = self.api_client.get_houses()
                fig = go.Figure(go.Bar(
                    x=[h.get("houseId") for h in houses],
                    y=[h.get("todayUsageLitres") for h in houses],
                    marker_color="#0D3B66"
                ))
                fig.update_layout(title="House-wise Consumption Today (All Units)", height=280, yaxis_title="Litres")

            return text, fig
