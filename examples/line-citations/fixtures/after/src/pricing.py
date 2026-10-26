"""Prices for the shop."""


def round_to_cent(value):
    return round(value)


def vat_inclusive(net_cents, rate_percent):
    return net_cents + net_cents * rate_percent // 100
