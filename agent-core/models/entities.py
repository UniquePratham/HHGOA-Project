from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    USER = "User"
    ACCOUNT = "Account"
    CARD = "Card"
    TRANSACTION = "Transaction"
    DEVICE = "Device"
    IP = "IP"
    EMAIL_DOMAIN = "EmailDomain"
    MERCHANT = "Merchant"
    CASE = "Case"


class Transaction(BaseModel):
    transaction_id: str
    amount: float
    timestamp: str
    card_id: str
    user_id: str
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    merchant_id: Optional[str] = None
    merchant_category: Optional[str] = None
    model_risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    channel: str = "online"  # online, pos, atm
    billing_country: str = "US"
    shipping_country: Optional[str] = "US"
    is_foreign_transaction: bool = False
    attributes: Dict[str, Any] = Field(default_factory=dict)


class Card(BaseModel):
    card_id: str
    user_id: str
    card_type: str = "credit"  # credit, debit, prepaid
    card_network: str = "visa"  # visa, mastercard, discover, amex
    issuer_bank: Optional[str] = None
    expiration_date: Optional[str] = None
    status: str = "active"  # active, blocked, frozen


class Device(BaseModel):
    device_id: str
    device_type: Optional[str] = "mobile"  # mobile, desktop, tablet
    os: Optional[str] = None
    browser: Optional[str] = None
    is_emulator: bool = False
    is_rooted_or_jailbroken: bool = False
    connected_accounts_count: int = 1


class IPAddress(BaseModel):
    ip: str
    country: str = "US"
    is_vpn_or_proxy: bool = False
    is_tor_node: bool = False
    reputation_score: float = 0.0  # 0.0 clean -> 100.0 malicious


class GraphNode(BaseModel):
    id: str
    label: str
    entity_type: EntityType
    properties: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)


class EgoGraph(BaseModel):
    center_node_id: str
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    hop_depth: int = 2
