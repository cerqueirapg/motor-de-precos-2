import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal


@dataclass
class Product:
    sku: str
    cost_price: Decimal
    min_margin: Decimal
    name: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CompetitorPriceLog:
    competitor_price: Decimal
    is_outlier: bool = False
    competitor_name: str | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class PricingHistory:
    sku: str
    calculated_price: Decimal
    effective_margin: Decimal
    status: str
    applied_iqr_filter: bool = False
    competitor_prices: list[CompetitorPriceLog] = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    calculated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
