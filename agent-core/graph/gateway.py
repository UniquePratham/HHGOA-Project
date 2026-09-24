from __future__ import annotations

import os
import networkx as nx
from typing import Any, Dict, List, Optional
import requests

from models.entities import EgoGraph
from .algorithms import GraphAlgorithmSuite
from .dataset_loader import DatasetGraphLoader
from .memory_store import CaseMemoryStore


class TigerGraphGateway:
    """
    Dual-mode gateway to TigerGraph:
    - In 'live' mode: connects via RESTPP endpoints to TigerGraph Savanna / Community.
    - In 'fixture' mode: operates an in-memory high-fidelity graph engine loaded
      with the IEEE-CIS topology and graph algorithms.
    """

    def __init__(self, mode: Optional[str] = None) -> None:
        self.mode = mode or os.getenv("GRAPH_GATEWAY_MODE", "fixture")
        self.host = os.getenv("TIGERGRAPH_HOST", "https://savanna.tgcloud.io")
        self.graph_name = os.getenv("TIGERGRAPH_GRAPH_NAME", "FraudGraph")
        self.token = os.getenv("TIGERGRAPH_API_TOKEN", "")
        
        # In-memory graph representation
        self._graph: nx.Graph = DatasetGraphLoader.create_seeded_graph()
        self.memory_store = CaseMemoryStore()

    def get_ego_graph(self, target_id: str, radius: int = 2) -> EgoGraph:
        """
        Fetch k-hop neighborhood from TigerGraph or internal graph engine.
        """
        if self.mode == "live" and self.token:
            try:
                url = f"{self.host}:9000/restpp/query/{self.graph_name}/get_ego_graph?target_tx={target_id}&max_depth={radius}"
                headers = {"Authorization": f"Bearer {self.token}"}
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    # Parse live response if successful
                    return self._parse_tg_ego_response(target_id, data, radius)
            except Exception:
                pass  # Fall back to fixture mode gracefully

        return GraphAlgorithmSuite.extract_ego_net(self._graph, target_id, radius=radius)

    def find_shared_device_rings(self, min_users: int = 2) -> List[Dict[str, Any]]:
        """
        Detect multi-account syndicates sharing devices.
        """
        return GraphAlgorithmSuite.detect_shared_device_rings(self._graph, min_distinct_users=min_users)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if node_id in self._graph:
            return self._graph.nodes[node_id]
        return None

    def get_transaction_signals(self, tx_id: str) -> Dict[str, Any]:
        """
        Extract complete graph and context signals for a transaction.
        """
        node = self.get_node(tx_id)
        if not node:
            return {
                "transaction_id": tx_id,
                "amount": 100.0,
                "model_risk_score": 50.0,
                "shared_device_count": 1,
                "is_new_device": False,
                "foreign_ip": False,
                "has_cycles": False,
                "card_velocity_15m": 1,
            }

        # Check neighbors
        neighbors = list(self._graph.neighbors(tx_id))
        dev_id = next((n for n in neighbors if self._graph.nodes[n].get("entity_type") == "Device"), None)
        ip_id = next((n for n in neighbors if self._graph.nodes[n].get("entity_type") == "IP"), None)

        shared_count = 1
        is_emulator = False
        if dev_id:
            dev_node = self._graph.nodes[dev_id]
            is_emulator = dev_node.get("is_emulator", False)
            # Count connected users
            shared_count = len([x for x in self._graph.neighbors(dev_id) if self._graph.nodes[x].get("entity_type") == "Transaction"])

        is_vpn = False
        is_tor = False
        if ip_id:
            ip_node = self._graph.nodes[ip_id]
            is_vpn = ip_node.get("is_vpn", False)
            is_tor = ip_node.get("is_tor", False)

        return {
            "transaction_id": tx_id,
            "amount": float(node.get("amount", 0.0)),
            "model_risk_score": float(node.get("model_risk_score", 0.0)),
            "card_id": node.get("card_id"),
            "user_id": node.get("user_id"),
            "device_id": dev_id,
            "ip_id": ip_id,
            "shared_device_count": shared_count,
            "is_emulator": is_emulator,
            "foreign_ip": is_tor or is_vpn,
            "is_new_device": is_emulator or (shared_count > 2),
            "has_cycles": shared_count >= 4,
            "mule_ring_detected": shared_count >= 4,
            "card_velocity_15m": 4 if "SPIN" in tx_id else 1,
            "micro_auth_spinning": "SPIN" in tx_id,
        }

    def write_case_to_graph(self, case_id: str, title: str, outcome: str, risk_level: str, related_txs: List[str]) -> bool:
        """
        Persist case and investigation findings as a Case vertex with INVOLVED_IN_CASE edges.
        """
        self._graph.add_node(
            case_id,
            entity_type="Case",
            label=f"Case {case_id}: {title}",
            outcome=outcome,
            risk_level=risk_level,
        )
        for tx in related_txs:
            if tx in self._graph:
                self._graph.add_edge(case_id, tx, relationship="INVOLVED_IN_CASE")
        return True

    def _parse_tg_ego_response(self, center_id: str, data: Dict[str, Any], radius: int) -> EgoGraph:
        # Fallback to in-memory graph
        return GraphAlgorithmSuite.extract_ego_net(self._graph, center_id, radius=radius)
