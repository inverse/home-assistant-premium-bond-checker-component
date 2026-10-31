from premium_bond_checker.client import BondPeriod


def redact_holder_number(holder_number: str) -> str:
    """Return a holder number safe for logs."""
    return f"{'*' * max(len(holder_number) - 1, 0)}{holder_number[-1:]}"


BOND_PERIOD_CONFIG = {
    "this_month": BondPeriod.THIS_MONTH,
    "last_six_months": BondPeriod.LAST_SIX_MONTHS,
    "unclaimed": BondPeriod.UNCLAIMED,
}

DOMAIN = "premium_bond_checker"

CONF_HOLDER_NUMBER = "holder_number"

COORDINATOR = "coordinator"

ATTR_HEADER = "header"
ATTR_TAGLINE = "tagline"
ATTR_REVEAL_BY = "reveal_by"
