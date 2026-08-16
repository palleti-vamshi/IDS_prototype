"""
SCADA API

Provides REST endpoints for the industrial SCADA dashboard.
"""

from fastapi import APIRouter

from backend.industrial.scada.dashboard import (
    SCADADashboard,
)


router = APIRouter(
    prefix="/scada",
    tags=["SCADA"],
)


scada_dashboard = SCADADashboard()
scada_dashboard.start()


@router.get("/latest")
def get_latest_scada_data():
    """Return the latest telemetry received by SCADA."""

    return scada_dashboard.get_latest_data()