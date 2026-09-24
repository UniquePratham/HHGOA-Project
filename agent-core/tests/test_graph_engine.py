import pytest
from graph.gateway import TigerGraphGateway
from graph.algorithms import GraphAlgorithmSuite


def test_gateway_initialization():
    gateway = TigerGraphGateway(mode="fixture")
    assert gateway.mode == "fixture"
    assert gateway._graph.number_of_nodes() > 10


def test_ego_graph_extraction():
    gateway = TigerGraphGateway(mode="fixture")
    ego = gateway.get_ego_graph("DEV_RING_888", radius=2)
    assert ego.center_node_id == "DEV_RING_888"
    assert len(ego.nodes) > 3
    assert len(ego.edges) > 3


def test_shared_device_ring_detection():
    gateway = TigerGraphGateway(mode="fixture")
    rings = gateway.find_shared_device_rings(min_users=2)
    assert len(rings) >= 1
    ring = rings[0]
    assert ring["device_id"] == "DEV_RING_888"
    assert ring["distinct_users_count"] >= 3


def test_case_memory_similarity_search():
    gateway = TigerGraphGateway(mode="fixture")
    # Vector: high risk, new device, shared ring, mule ring, foreign IP
    query_vector = [0.95, 1.0, 0.8, 0.8, 0.9, 1.0]
    matches = gateway.memory_store.find_similar_cases(query_vector, top_k=2)
    assert len(matches) > 0
    assert matches[0]["similarity_score"] > 0.8


def test_write_case_to_graph():
    gateway = TigerGraphGateway(mode="fixture")
    ok = gateway.write_case_to_graph("CASE_999", "Test Ring Case", "CONFIRMED_FRAUD", "CRITICAL", ["TX_RING_103"])
    assert ok is True
    node = gateway.get_node("CASE_999")
    assert node is not None
    assert node["entity_type"] == "Case"
