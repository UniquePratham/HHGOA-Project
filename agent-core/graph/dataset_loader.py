from __future__ import annotations

import networkx as nx
from typing import Any, Dict, List, Tuple


class DatasetGraphLoader:
    """
    Constructs and seeds the IEEE-CIS fraud knowledge graph with users, accounts,
    cards, devices, IPs, and transactions.
    """

    @classmethod
    def create_seeded_graph(cls) -> nx.Graph:
        g = nx.Graph()

        # Seed 10 Users and Accounts
        users = [
            ("USR_101", "Alice Smith", 12.0),
            ("USR_102", "Bob Jones", 25.0),
            ("USR_103", "Charlie Brown", 88.0),
            ("USR_104", "David Miller", 94.0),
            ("USR_105", "Emma Wilson", 15.0),
            ("USR_106", "Frank Wright", 72.0),
            ("USR_107", "Grace Hopper", 10.0),
            ("USR_108", "Henry Ford", 82.0),
            ("USR_109", "Isabella Garcia", 91.0),
            ("USR_110", "Jack Taylor", 30.0),
        ]

        for u_id, name, risk in users:
            g.add_node(
                u_id,
                entity_type="User",
                label=name,
                risk_level="CRITICAL" if risk > 85 else ("HIGH" if risk > 65 else "LOW"),
                risk_score=risk,
            )
            acc_id = f"ACC_{u_id[4:]}"
            g.add_node(
                acc_id,
                entity_type="Account",
                label=f"Account {acc_id}",
                status="active",
            )
            g.add_edge(u_id, acc_id, relationship="OWNS")

            # Attach a Card
            card_id = f"CARD_{u_id[4:]}"
            g.add_node(
                card_id,
                entity_type="Card",
                label=f"Visa ending {card_id[-4:]}",
                status="active",
                card_type="credit",
            )
            g.add_edge(acc_id, card_id, relationship="USES_CARD")

        # Seed Devices (including fraud ring shared device)
        g.add_node("DEV_SAFE_01", entity_type="Device", label="iPhone 15", is_emulator=False)
        g.add_node("DEV_SAFE_02", entity_type="Device", label="MacBook Pro", is_emulator=False)
        g.add_node("DEV_RING_888", entity_type="Device", label="NoxPlayer Emulator", is_emulator=True, risk_level="CRITICAL")

        # Seed IPs
        g.add_node("IP_RES_01", entity_type="IP", label="198.51.100.12 (Residential)", is_vpn=False)
        g.add_node("IP_TOR_99", entity_type="IP", label="185.220.101.5 (Tor Exit Node)", is_tor=True, is_vpn=True, risk_level="CRITICAL")

        # Seed Fraud Ring Links: USR_103, USR_104, USR_108, USR_109 all share DEV_RING_888 and IP_TOR_99
        ring_users = ["USR_103", "USR_104", "USR_108", "USR_109"]
        for u in ring_users:
            c = f"CARD_{u[4:]}"
            tx_id = f"TX_RING_{u[4:]}"
            g.add_node(
                tx_id,
                entity_type="Transaction",
                label=f"Tx {tx_id} ($4,900.00)",
                amount=4900.0,
                model_risk_score=92.5,
                card_id=c,
                user_id=u,
                channel="online",
            )
            g.add_edge(c, tx_id, relationship="PERFORMED_TRANSACTION")
            g.add_edge(tx_id, "DEV_RING_888", relationship="ASSOCIATED_DEVICE")
            g.add_edge(tx_id, "IP_TOR_99", relationship="CONNECTED_IP")

        # Seed Standard Transactions for USR_101 (Safe)
        g.add_node(
            "TX_SAFE_101",
            entity_type="Transaction",
            label="Tx SAFE ($45.20)",
            amount=45.20,
            model_risk_score=8.5,
            card_id="CARD_101",
            user_id="USR_101",
            channel="pos",
        )
        g.add_edge("CARD_101", "TX_SAFE_101", relationship="PERFORMED_TRANSACTION")
        g.add_edge("TX_SAFE_101", "DEV_SAFE_01", relationship="ASSOCIATED_DEVICE")
        g.add_edge("TX_SAFE_101", "IP_RES_01", relationship="CONNECTED_IP")

        # Seed Micro-Spinning Sequence for USR_106
        for i in range(1, 5):
            tx_spin = f"TX_SPIN_{i}"
            amt = 1.25 if i < 4 else 850.00
            g.add_node(
                tx_spin,
                entity_type="Transaction",
                label=f"Tx Spin {i} (${amt})",
                amount=amt,
                model_risk_score=88.0 if i == 4 else 75.0,
                card_id="CARD_106",
                user_id="USR_106",
                channel="online",
            )
            g.add_edge("CARD_106", tx_spin, relationship="PERFORMED_TRANSACTION")
            g.add_edge(tx_spin, "DEV_RING_888", relationship="ASSOCIATED_DEVICE")

        return g
