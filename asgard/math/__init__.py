from decimal import Decimal, ROUND_UP


def round_up(n: Decimal, prec: int = 2) -> float:
    return float(n.quantize(Decimal("." + "0" * prec), rounding=ROUND_UP))
