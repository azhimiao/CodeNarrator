"""Configuration for the small record-report project."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    minimum: float = 0.8
    limit: int = 3

    def __post_init__(self):
        if not 0 <= self.minimum <= 1:
            raise ValueError("minimum must be between zero and one")
        if self.limit < 1:
            raise ValueError("limit must be positive")
