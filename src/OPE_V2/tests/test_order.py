import pytest 
from datetime import datetime, timezone

from bot.order.order import Order, OrderSide
from event.event import EventType


# ───────────────────────────────
# 🔹 FIXTURES POUR DIFFÉRENTS CAS
# ───────────────────────────────

@pytest.fixture
def valid_order_created_buy() -> Order:
    return Order(
        created_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        level=1000.0,
        asset_qty=1.0,
        side=OrderSide.LONG,
        leverage=3.0,
        tp_pct=0.1,
        sl_pct=0.05,
        order_event=EventType.ORDER_CREATED
    )

@pytest.fixture
def order_no_tp_sl() -> Order:
    return Order(
        created_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        level=500.0,
        asset_qty=2.0,
        side=OrderSide.SHORT,
        leverage=2.0,
        tp_pct=None,
        sl_pct=None,
        order_event=EventType.ORDER_CREATED
    )

def test_tp_price(valid_order_created_buy:Order) -> None:
    assert valid_order_created_buy.tp_price == 1100.0

def test_sl_price(valid_order_created_buy:Order) -> None:
    assert valid_order_created_buy.sl_price == 950.0

def test_no_tp_returns_none(order_no_tp_sl:Order) -> None:
    assert order_no_tp_sl.tp_price is None

def test_no_sl_returns_none(order_no_tp_sl:Order) -> None:
    assert order_no_tp_sl.sl_price is None

# ───────────────────────────────
# 🔹 TEST RAISE TYPEERROR
# ───────────────────────────────

@pytest.mark.parametrize(
    "field, value, match",
    [
        ("created_at", 12.34, "created_at must be int.*"),
        ("level", "100", "level must be float.*"),
        ("asset_qty", "a", "asset_qty must be float.*"),
        ("leverage", None, "leverage must be float.*"),
        ("side", "BUY", "side must be an instance of OrderSide.*"),
        ("order_event", 123, "order_event must be an instance of EventType.*"),
        ("executed_at", 123.0, "executed_at must be int or None.*"),
        ("tp_pct", 123, "tp_pct must be float or None.*"),
        ("sl_pct", 123, "sl_pct must be float or None.*"),
        
    ]
)
def test_invalid_types(field, value, match):
    kwargs = dict(
        created_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        level=1000.0,
        asset_qty=1.0,
        side=OrderSide.BUY,
        leverage=2.0,
        tp_pct=0.1,
        sl_pct=0.1,
        order_event=EventType.ORDER_CREATED
    )
    kwargs[field] = value
    with pytest.raises(TypeError, match=match):
        Order(**kwargs)


# ───────────────────────────────
# 🔹 TEST DE RAISE VALUEERROR
# ───────────────────────────────

@pytest.mark.parametrize(
    "field, value, match",
    [
        ("level", -10.0, "level .* must be greater or equal to 0"),
        ("asset_qty", -1.0, "asset_qty .* must be greater or equal to 0"),
        ("leverage", -0.1, "leverage .* must be greater or equal to 0"),
        ("tp_pct", -1.5, "tp_pct .* must be greater than 0"),
        ("sl_pct", -0.1, "sl_pct .* must be greater than 0"),
    ]
)
def test_invalid_fields(field, value, match):
    kwargs = dict(
        created_at=int(datetime.now(timezone.utc).timestamp() * 1000),
        level=1000.0,
        asset_qty=1.0,
        side=OrderSide.BUY,
        leverage=2.0,
        tp_pct=0.1,
        sl_pct=0.1,
        order_event=EventType.ORDER_CREATED
    )
    kwargs[field] = value
    with pytest.raises(ValueError, match=match):
        Order(**kwargs)
