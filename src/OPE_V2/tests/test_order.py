import pytest 
from OPE_V2.order import Order, OrderSide, OrderEvent


# ───────────────────────────────
# 🔹 FIXTURES POUR DIFFÉRENTS CAS
# ───────────────────────────────

@pytest.fixture
def valid_order() -> Order:
    return Order(
        id=1,
        level=1000.0,
        asset_qty=1.0,
        quote_qty=1000.0,
        side=OrderSide.BUY,
        leverage=3,
        tp_pct=0.1,
        sl_pct=0.05,
        event=OrderEvent.OPEN
    )

@pytest.fixture
def order_no_tp_sl() -> Order:
    return Order(
        id=2,
        level=500.0,
        asset_qty=2.0,
        quote_qty=1000.0,
        side=OrderSide.SELL,
        leverage=2,
        tp_pct=None,
        sl_pct=None,
        event=OrderEvent.OPEN
    )

def test_tp_price(valid_order) -> None:
    assert valid_order.tp_price == 1100.0

def test_sl_price(valid_order) -> None:
    assert valid_order.sl_price == 950.0

def test_no_tp_returns_none(order_no_tp_sl) -> None:
    assert order_no_tp_sl.tp_price is None

def test_no_sl_returns_none(order_no_tp_sl) -> None:
    assert order_no_tp_sl.sl_price is None

# ───────────────────────────────
# 🔹 TEST RAISE VALUEERROR
# ───────────────────────────────


@pytest.mark.parametrize(
    "field, value, match",
    [
        ("level", -10, "level .* must be greater or equal to zero"),
        ("asset_qty", -1, "asset_qty .* must be greater or equal to zero"),
        ("quote_qty", -100, "quote_qty .* must be greater or equal to zero"),
        ("leverage", 0.5, "leverage .* must be greater or equal to 1"),
        ("tp_pct", -1.5, "tp_pct .* must be greater than 0"),
        ("sl_pct", -0.1, "sl_pct .* must be greater than 0"),
    ]
)
def test_invalid_fields(field, value, match):
    kwargs = dict(
        id=1,
        level=1000,
        asset_qty=1,
        quote_qty=1000,
        side=OrderSide.BUY,
        leverage=2,
        tp_pct=0.1,
        sl_pct=0.1,
        event=OrderEvent.OPEN
    )
    kwargs[field] = value
    with pytest.raises(ValueError, match=match):
        Order(**kwargs)