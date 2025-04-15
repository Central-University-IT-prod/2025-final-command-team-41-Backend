from pydantic.dataclasses import dataclass


@dataclass
class HealthCheckSchema:
    fact_check_status: str = 'True ✅'
