import pytest 
from OPE_V2.position import Position, PositionSide, PositionEvent
from datetime import datetime, timezone

# ───────────────────────────────
# 🔹 FIXTURES POUR DIFFÉRENTS CAS
# ───────────────────────────────

@pytest.fixture
def valid_position_long() -> Position:
    return Position(
        id = 1,
        entry_at = int(datetime.now(timezone.utc).timestamp() * 1000),
        entry_price = 1000.0,
        asset_qty = 1.0,
        side = PositionSide.LONG,
        event = PositionEvent.OPEN,
        tp_price = 1200.0,
        sl_price = 900.0,
        )

@pytest.fixture
def valid_position_short() -> Position:
    return Position(
        id = 2,
        entry_at = int(datetime.now(timezone.utc).timestamp() * 1000),
        entry_price = 1000.0,
        asset_qty = 1.0,
        side = PositionSide.SHORT,
        event = PositionEvent.OPEN,
        tp_price = 800.0,
        sl_price = 1100.0,
        )

def test_pnl_valid_position_long(valid_position_long):
    assert valid_position_long.pnl(1100.0) == 10.0
    assert valid_position_long.pnl(950.0) == -5.0

def test_pnl_valid_position_short(valid_position_short):
    assert valid_position_short.pnl(900.0) == 10
    assert valid_position_short.pnl(1050.0) == -5.0