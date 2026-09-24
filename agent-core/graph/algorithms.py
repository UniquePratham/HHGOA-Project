from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple
import networkx as nx
from models.entities import EgoGraph, EntityType, GraphEdge, GraphNode


class GraphAlgorithmSuite:
    """
    Graph algorithms for fraud ring detection, ego-net traversal,
    cycle identification, and network centrality.
    """

    @staticmethod
    def extract_ego_net(
        graph: nx.Graph,
        center_node_id: str,
        radius: int = 2,
    ) -> EgoGraph:
        """
        Extract k-hop ego network around the center node.
        """
        if center_node_id not in graph:
            return EgoGraph(center_node_id=center_node_id, nodes=[], edges=[], hop_depth=radius)

        ego = nx.ego_graph(graph, center_node_id, radius=radius)
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        for node_id, attrs in ego.nodes(data=True):
            entity_type_str = attrs.get("entity_type", "Transaction")
            try:
                entity_type = EntityType(entity_type_str)
            except ValueError:
                entity_type = EntityType.TRANSACTION

            nodes.append(
                GraphNode(
                    id=str(node_id),
                    label=str(attrs.get("label", node_id)),
                    entity_type=entity_type,
                    properties=attrs,
                    risk_level=attrs.get("risk_level", "LOW"),
                )
            )

        for u, v, attrs in ego.edges(data=True):
            edges.append(
                GraphEdge(
                    source=str(u),
                    target=str(v),
                    relationship=str(attrs.get("relationship", "CONNECTED_TO")),
                    weight=float(attrs.get("weight", 1.0)),
                    properties=attrs,
                )
            )

        return EgoGraph(center_node_id=center_node_id, nodes=nodes, edges=edges, hop_depth=radius)

    @staticmethod
    def detect_shared_device_rings(
        graph: nx.Graph,
        min_distinct_users: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Find device nodes that connect to multiple distinct users/cards, forming a fraud ring.
        """
        rings: List[Dict[str, Any]] = []
        
        device_nodes = [
            n for n, d in graph.nodes(data=True)
            if d.get("entity_type") == "Device"
        ]

        for dev in device_nodes:
            neighbors = list(graph.neighbors(dev))
            connected_cards: Set[str] = set()
            connected_users: Set[str] = set()

            for n in neighbors:
                n_type = graph.nodes[n].get("entity_type")
                if n_type == "Transaction":
                    card_id = graph.nodes[n].get("card_id")
                    user_id = graph.nodes[n].get("user_id")
                    if card_id:
                        connected_cards.add(card_id)
                    if user_id:
                        connected_users.add(user_id)
                elif n_type == "Card":
                    connected_cards.add(n)
                elif n_type == "User":
                    connected_users.add(n)

            if len(connected_users) >= min_distinct_users or len(connected_cards) >= 3:
                rings.append({
                    "device_id": dev,
                    "device_props": graph.nodes[dev],
                    "distinct_users_count": len(connected_users),
                    "distinct_cards_count": len(connected_cards),
                    "users": list(connected_users),
                    "cards": list(connected_cards),
                    "ring_severity": "CRITICAL" if len(connected_users) >= 4 else "HIGH",
                })

        return rings

    @staticmethod
    def detect_directed_cycles(
        digraph: nx.DiGraph,
        max_cycle_len: int = 4,
    ) -> List[List[str]]:
        """
        Detect circular transaction paths (smurfing / mule chains).
        """
        cycles: List[List[str]] = []
        try:
            simple_cycles = nx.simple_cycles(digraph)
            for c in simple_cycles:
                if 2 <= len(c) <= max_cycle_len:
                    cycles.append([str(x) for x in c])
        except Exception:
            pass
        return cycles

    @staticmethod
    def calculate_velocity_signals(
        transactions: List[Dict[str, Any]],
        window_minutes: int = 60,
    ) -> Dict[str, Any]:
        """
        Compute transaction velocity and micro-spinning indicators.
        """
        if not transactions:
            return {"tx_count": 0, "total_amount": 0.0, "micro_auth_count": 0}

        amounts = [float(t.get("amount", 0.0)) for t in transactions]
        micro_auths = [a for a in amounts if 0.0 < a <= 5.0]

        return {
            "tx_count": len(transactions),
            "total_amount": sum(amounts),
            "avg_amount": sum(amounts) / len(amounts),
            "micro_auth_count": len(micro_auths),
            "has_micro_auth_spinning": len(micro_auths) >= 3,
        }
