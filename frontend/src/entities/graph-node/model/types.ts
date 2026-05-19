/**
 * Graph node and edge types for React Flow
 */

import type { Node, Edge } from 'reactflow';

// Node data structure
export interface NodeData {
  label: string;
  type: string;
  description?: string;
  properties?: Record<string, unknown>;
  aliases?: string[];
  degree?: number;
  component_id?: number | null;
  is_isolated?: boolean;
  is_in_largest_component?: boolean;
  generated_from_relationship?: boolean;
}

// Edge data structure
export interface EdgeData {
  weight: number;
  properties?: Record<string, unknown>;
  original_source?: string | null;
  original_target?: string | null;
  endpoint_resolved?: boolean;
}

// React Flow node type
export type GraphNode = Node<NodeData>;

// React Flow edge type
export type GraphEdge = Edge<EdgeData>;

// Full graph structure from API
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: Record<string, unknown>;
}

// Graph statistics
export interface GraphStats {
  entity_count: number;
  relationship_count: number;
  indexed: boolean;
  last_indexed_at?: string;
}

// Node position
export interface NodePosition {
  x: number;
  y: number;
}

// API response format (before transformation to React Flow)
export interface GraphApiNode {
  id: string;
  data: NodeData;
  position: NodePosition;
  type: string;
}

export interface GraphApiEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  data: EdgeData;
}

export interface GraphApiResponse {
  nodes: GraphApiNode[];
  edges: GraphApiEdge[];
  metadata?: Record<string, unknown>;
}
