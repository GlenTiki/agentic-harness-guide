from . import bills, bills_stop, doi, injection, missing_month, plug, reviewer, sycophancy

REGISTRY = {
    "bills": bills.grade,
    "bills_stop": bills_stop.grade,
    "doi": doi.grade,
    "injection": injection.grade,
    "missing_month": missing_month.grade,
    "plug": plug.grade,
    "reviewer": reviewer.grade,
    "sycophancy": sycophancy.grade,
}
