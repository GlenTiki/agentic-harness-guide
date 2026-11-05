"""Prices for the shop."""

def vat_inclusive(net_cents, rate_percent):
    return net_cents + net_cents * rate_percent // 100


def round_to_cent(value):
    return round(value)
