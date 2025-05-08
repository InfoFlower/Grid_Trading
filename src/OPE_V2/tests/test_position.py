import pytest 
from OPE_V2.bot.position import Position, PositionSide, PositionEvent
from datetime import datetime, timezone

# ───────────────────────────────
# 🔹 FIXTURES POUR DIFFÉRENTS CAS
# ───────────────────────────────

@pytest.fixture
def valid_position_long() -> Position:
    return Position(
        entry_at = int(datetime.now(timezone.utc).timestamp() * 1000),
        entry_price = 1000.0,
        asset_qty = 1.0,
        leverage = 1.4,
        side = PositionSide.LONG,
        position_event = PositionEvent.OPENED,
        tp_price = 1200.0,
        sl_price = 900.0,
        )

@pytest.fixture
def valid_position_short() -> Position:
    return Position(
        entry_at = int(datetime.now(timezone.utc).timestamp() * 1000),
        entry_price = 1000.0,
        asset_qty = 1.0,
        leverage = 2.4,
        side = PositionSide.SHORT,
        position_event = PositionEvent.OPENED,
        tp_price = 800.0,
        sl_price = 1100.0,
        )

def test_pnl_valid_position_long(valid_position_long):
    assert valid_position_long.pnl(1100.0) == 10.0
    assert valid_position_long.pnl(950.0) == -5.0

def test_pnl_valid_position_short(valid_position_short):
    assert valid_position_short.pnl(900.0) == 10
    assert valid_position_short.pnl(1050.0) == -5.0

# ───────────────────────────────
# 🔹 TEST RAISE TYPEERROR
# ───────────────────────────────
#     
@pytest.mark.parametrize(
    "field, value, match",
    [
        ("entry_at", 12.34, "entry_at must be int.*"),
        ("closed_at", "not-an-int", "closed_at must be int or None.*"),
        ("entry_price", "100.0", "entry_price must be float.*"),
        ("asset_qty", "qty", "asset_qty must be float.*"),
        ("leverage", 2, "leverage must be float.*"),
        ("side", "LONG", "side must be an instance of PositionSide.*"),
        ("position_event", 999, "position_event must be an instance of PositionEvent.*"),
        ("close_price", "150.0", "close_price must be float or None.*"),
        ("tp_price", True, "tp_price must be float or None.*"),
        ("sl_price", "stop", "sl_price must be float or None.*"),
    ]
)
def test_position_invalid_types(field, value, match):
    kwargs = dict(
        entry_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        closed_at=None,
        entry_price=100.0,
        asset_qty=1.0,
        leverage = 2.4,
        side=PositionSide.LONG,
        position_event=PositionEvent.OPENED,
        close_price=None,
        tp_price=None,
        sl_price=None
    )
    kwargs[field] = value
    with pytest.raises(TypeError, match=match):
        Position(**kwargs)

# ───────────────────────────────
# 🔹 TEST DE RAISE VALUEERROR
# ───────────────────────────────

@pytest.mark.parametrize(
    "field, value, match",
    [
        ("entry_price", -10.0, "entry_price .* must be greater or equal to 0"),
        ("asset_qty", -1.0, "asset_qty .* must be greater or equal to 0"),
        ("close_price", -1.0, "close_price .* must be greater or equal to 0"),
        ("leverage", -1.0, "leverage .* must be greater or equal to 0"),
        
        # ("tp_pct", -1.5, "tp_pct .* must be greater than 0"),
        # ("sl_pct", -0.1, "sl_pct .* must be greater than 0"),
    ]
)
def test_invalid_fields(field, value, match):
    kwargs = dict(
        entry_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        entry_price=1000.0,
        asset_qty=1.0,
        leverage = 2.4,
        side=PositionSide.LONG,
        position_event=PositionEvent.OPENED,
        tp_price=1100.0,
        sl_price=950.0
    )
    kwargs[field] = value
    with pytest.raises(ValueError, match=match):
        Position(**kwargs)

# Check le raise des ValueError sur tp_price
# tp_price
@pytest.mark.parametrize(
    "side, entry_price, tp_price, expected_msg",
    [
        (PositionSide.LONG, 100.0, 90.0, r"Side:PositionSide\.LONG;TP=90\.0 < EP=100\.0;TP must be greater.*"),  # TP < EP for LONG => Erreur
        (PositionSide.SHORT, 100.0, 110.0, r"Side:PositionSide\.SHORT;TP=110\.0 > EP=100\.0;TP must be lower.*"),  # TP > EP for SHORT => Erreur
    ]
)
def test_invalid_tp_price_for_side(side, entry_price, tp_price, expected_msg):
    with pytest.raises(ValueError, match=expected_msg):
        Position(
            entry_at=1234567890000,
            closed_at=None,
            entry_price=entry_price,
            asset_qty=1.0,
            leverage = 2.4,
            side=side,
            position_event=PositionEvent.OPENED,
            close_price=None,
            tp_price=tp_price,
            sl_price=None
        )

# sl_price
@pytest.mark.parametrize(
    "side, entry_price, sl_price, expected_msg",
    [
        (PositionSide.LONG, 100.0, 110.0, r"Side:PositionSide\.LONG;SL=110\.0 > EP=100\.0;SL must be lower.*"),  # SL > EP for LONG => Erreur
        (PositionSide.SHORT, 100.0, 90.0, r"Side:PositionSide\.SHORT;SL=90\.0 < EP=100\.0;SL must be greater.*"),  # SL < EP for SHORT => Erreur
    ]
)
def test_invalid_sl_price_for_side(side, entry_price, sl_price, expected_msg):
    with pytest.raises(ValueError, match=expected_msg):
        Position(
            entry_at=1234567890000,
            closed_at=None,
            entry_price=entry_price,
            asset_qty=1.0,
            leverage = 2.4,
            side=side,
            position_event=PositionEvent.OPENED,
            close_price=None,
            tp_price=None,
            sl_price=sl_price
        )