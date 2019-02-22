from decimal import Decimal, ROUND_UP


def round_up(n: Decimal, prec: int = 2) -> Decimal:
    return n.quantize(Decimal("." + "0" * prec), rounding=ROUND_UP)
