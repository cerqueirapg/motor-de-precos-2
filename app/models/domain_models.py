import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TenantModel(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    products: Mapped[list["ProductModel"]] = relationship(
        "ProductModel", back_populates="tenant", cascade="all, delete-orphan"
    )
    pricing_histories: Mapped[list["PricingHistoryModel"]] = relationship(
        "PricingHistoryModel", back_populates="tenant", cascade="all, delete-orphan"
    )


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(150))
    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    min_margin: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    tenant: Mapped["TenantModel"] = relationship(
        "TenantModel", back_populates="products"
    )
    pricing_histories: Mapped[list["PricingHistoryModel"]] = relationship(
        "PricingHistoryModel", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_tenant_sku", "tenant_id", "sku", unique=True),)


class PricingHistoryModel(Base):
    __tablename__ = "pricing_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    calculated_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    effective_margin: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    applied_iqr_filter: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    tenant: Mapped["TenantModel"] = relationship(
        "TenantModel", back_populates="pricing_histories"
    )
    product: Mapped["ProductModel"] = relationship(
        "ProductModel", back_populates="pricing_histories"
    )
    competitor_prices: Mapped[list["CompetitorPriceLogModel"]] = relationship(
        "CompetitorPriceLogModel",
        back_populates="pricing_history",
        cascade="all, delete-orphan",
    )


class CompetitorPriceLogModel(Base):
    __tablename__ = "competitor_prices_log"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pricing_history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pricing_history.id", ondelete="CASCADE"),
        nullable=False,
    )
    competitor_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_outlier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    pricing_history: Mapped["PricingHistoryModel"] = relationship(
        "PricingHistoryModel", back_populates="competitor_prices"
    )
