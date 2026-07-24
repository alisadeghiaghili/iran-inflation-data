"""Data fetchers for Iran inflation data."""
from .world_bank import fetch_world_bank
from .imf import fetch_imf
from .cbi import fetch_cbi

__all__ = ["fetch_world_bank", "fetch_imf", "fetch_cbi"]
