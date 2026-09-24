"use client";

import React, { useEffect, useRef, useState, useMemo } from "react";

export interface GraphNode {
  id: string;
  label: string;
  entity_type: string;
  risk_level?: string;
  properties?: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  relationship: string;
}

interface EgoGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  highlightedEntityId?: string | null;
  onSelectNode?: (nodeId: string) => void;
}

export default function GraphViewer({
  nodes,
  edges,
  highlightedEntityId,
  onSelectNode,
}: EgoGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("ALL");
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Update selection if externally highlighted
  useEffect(() => {
    if (highlightedEntityId) {
      setSelectedNodeId(highlightedEntityId);
    }
  }, [highlightedEntityId]);

  // Filtered nodes
  const visibleNodes = useMemo(() => {
    if (filterType === "ALL") return nodes;
    return nodes.filter(
      (n) => n.entity_type.toUpperCase() === filterType || n.id === nodes[0]?.id
    );
  }, [nodes, filterType]);

  const visibleNodeIds = useMemo(
    () => new Set(visibleNodes.map((n) => n.id)),
    [visibleNodes]
  );

  const visibleEdges = useMemo(() => {
    return edges.filter(
      (e) => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)
    );
  }, [edges, visibleNodeIds]);

  const activeNode = useMemo(() => {
    const target = selectedNodeId || highlightedEntityId;
    return nodes.find((n) => n.id === target) || null;
  }, [nodes, selectedNodeId, highlightedEntityId]);

  // Canvas drawing loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();
    ctx.translate(panOffset.x, panOffset.y);
    ctx.scale(zoomLevel, zoomLevel);

    const center = { x: canvas.width / (2 * zoomLevel), y: canvas.height / (2 * zoomLevel) };
    const radius = Math.min(canvas.width, canvas.height) * 0.35;
    const posMap: Record<string, { x: number; y: number }> = {};

    visibleNodes.forEach((n, i) => {
      if (i === 0) {
        posMap[n.id] = { x: center.x, y: center.y };
      } else {
        const count = Math.max(1, visibleNodes.length - 1);
        const angle = ((i - 1) / count) * 2 * Math.PI;
        posMap[n.id] = {
          x: center.x + radius * Math.cos(angle),
          y: center.y + radius * Math.sin(angle),
        };
      }
    });

    // Edges
    visibleEdges.forEach((e) => {
      const p1 = posMap[e.source];
      const p2 = posMap[e.target];
      if (p1 && p2) {
        ctx.strokeStyle = "#334155";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
    });

    // Nodes
    visibleNodes.forEach((n) => {
      const p = posMap[n.id];
      if (!p) return;

      const isSelected = (selectedNodeId || highlightedEntityId) === n.id;
      let color = "#2563eb";
      if (n.entity_type === "Device") color = "#d97706";
      if (n.entity_type === "IP") color = "#ec4899";
      if (n.entity_type === "Card") color = "#8b5cf6";
      if (n.entity_type === "Transaction") color = "#0284c7";

      if (isSelected) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 16, 0, 2 * Math.PI);
        ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, isSelected ? 12 : 9, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = isSelected ? 2 : 1;
      ctx.stroke();

      ctx.fillStyle = "#94a3b8";
      ctx.font = isSelected ? "bold 10px monospace" : "9px monospace";
      ctx.textAlign = "center";
      const shortLabel = n.label.length > 12 ? n.label.slice(0, 10) + ".." : n.label;
      ctx.fillText(shortLabel, p.x, p.y + 18);
    });

    ctx.restore();
  }, [visibleNodes, visibleEdges, selectedNodeId, highlightedEntityId, zoomLevel, panOffset]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const clickX = (e.clientX - rect.left - panOffset.x) / zoomLevel;
    const clickY = (e.clientY - rect.top - panOffset.y) / zoomLevel;

    const center = { x: canvas.width / (2 * zoomLevel), y: canvas.height / (2 * zoomLevel) };
    const radius = Math.min(canvas.width, canvas.height) * 0.35;

    let foundId: string | null = null;
    visibleNodes.forEach((n, i) => {
      let x = center.x;
      let y = center.y;
      if (i > 0) {
        const count = Math.max(1, visibleNodes.length - 1);
        const angle = ((i - 1) / count) * 2 * Math.PI;
        x = center.x + radius * Math.cos(angle);
        y = center.y + radius * Math.sin(angle);
      }
      if (Math.hypot(clickX - x, clickY - y) <= 18) {
        foundId = n.id;
      }
    });

    if (foundId) {
      setSelectedNodeId(foundId);
      if (onSelectNode) onSelectNode(foundId);
    }
  };

  return (
    <div className="flex flex-col border-b border-[#262c37] p-4 bg-[#171b22]">
      {/* Controls */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Ego-Net Graph
        </span>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="bg-[#101318] border border-[#262c37] text-xs text-slate-200 px-2 py-0.5 rounded"
        >
          <option value="ALL">All Entities</option>
          <option value="CARD">Cards Only</option>
          <option value="DEVICE">Devices Only</option>
          <option value="IP">IPs Only</option>
          <option value="TRANSACTION">Transactions</option>
        </select>
      </div>

      {/* Canvas */}
      <div className="border border-[#262c37] bg-[#101318] relative">
        <canvas
          ref={canvasRef}
          width={320}
          height={260}
          onClick={handleCanvasClick}
          onMouseDown={(e) => {
            setIsDragging(true);
            setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
          }}
          onMouseMove={(e) => {
            if (!isDragging) return;
            setPanOffset({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
          }}
          onMouseUp={() => setIsDragging(false)}
          onMouseLeave={() => setIsDragging(false)}
          className="block w-full h-[260px] cursor-grab active:cursor-grabbing"
        />
      </div>

      <div className="flex justify-between items-center text-[10px] text-slate-500 mt-1">
        <span>Click node to inspect forensic attributes</span>
        <button
          onClick={() => {
            setZoomLevel(1.0);
            setPanOffset({ x: 0, y: 0 });
          }}
          className="underline text-sky-400"
        >
          Reset View
        </button>
      </div>

      {/* Contextual Inspector */}
      <div className="mt-4 pt-3 border-t border-[#262c37]">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
          Contextual Inspector
        </div>
        {activeNode ? (
          <div>
            <div className="font-mono text-sm font-bold text-slate-100">{activeNode.label}</div>
            <div className="flex justify-between text-xs py-1 border-b border-[#1c212a] mt-1 text-slate-400">
              <span>Entity Type</span>
              <span className="text-slate-200 font-medium">{activeNode.entity_type}</span>
            </div>
            <div className="flex justify-between text-xs py-1 border-b border-[#1c212a] text-slate-400">
              <span>Risk Status</span>
              <span className="font-mono text-amber-400">{activeNode.risk_level || "EVALUATED"}</span>
            </div>
            <div className="flex justify-between text-xs py-1 border-b border-[#1c212a] text-slate-400">
              <span>Graph Connections</span>
              <span className="font-mono text-slate-200">
                {edges.filter((e) => e.source === activeNode.id || e.target === activeNode.id).length} links
              </span>
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-500 mt-1">
            Click any vertex on the canvas or an evidence item to inspect details.
          </div>
        )}
      </div>
    </div>
  );
}
