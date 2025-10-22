"""
Procesar mapa editado manualmente
"""

import cv2
import numpy as np
from skimage.morphology import skeletonize
from sklearn.cluster import DBSCAN
from pathlib import Path
import pickle

class EditedMapProcessor:
    def __init__(self, edited_map_path):
        self.edited_map_path = edited_map_path
        self.original_map = cv2.imread('data/maps/mantis_hive_map.png')
        self.edited_map = None
        self.skeleton = None
        self.graph = None
    
    def load_edited_map(self):
        """Cargar mapa editado"""
        print("\n[1/4] Cargando mapa editado...")
        
        self.edited_map = cv2.imread(self.edited_map_path, cv2.IMREAD_GRAYSCALE)
        
        if self.edited_map is None:
            raise FileNotFoundError(f"No se encontró: {self.edited_map_path}")
        
        # Asegurar que sea binario
        _, self.edited_map = cv2.threshold(self.edited_map, 127, 255, cv2.THRESH_BINARY)
        
        coverage = (np.sum(self.edited_map > 0) / self.edited_map.size) * 100
        print(f"  ✓ Mapa cargado")
        print(f"  📊 Cobertura de caminos: {coverage:.1f}%")
        
        return self.edited_map
    
    def create_skeleton(self):
        """Crear skeleton"""
        print("\n[2/4] Creando skeleton...")
        
        binary = (self.edited_map > 0).astype(np.uint8)
        skeleton = skeletonize(binary)
        self.skeleton = (skeleton * 255).astype(np.uint8)
        
        # Visualización
        overlay = self.original_map.copy()
        overlay[self.skeleton > 0] = [0, 255, 0]
        
        cv2.imwrite('output/skeleton_from_edited.png', self.skeleton)
        cv2.imwrite('output/skeleton_overlay_edited.png', overlay)
        
        print("  ✓ Skeleton creado")
        return self.skeleton
    
    def find_nodes(self):
        """Detectar nodos"""
        print("\n[3/4] Detectando nodos...")
        
        # Contar vecinos
        kernel = np.ones((3, 3), np.uint8)
        kernel[1, 1] = 0
        neighbor_count = cv2.filter2D(self.skeleton // 255, -1, kernel)
        
        # Intersecciones (3+ vecinos)
        intersections = (self.skeleton > 0) & (neighbor_count >= 3)
        intersection_coords = np.column_stack(np.where(intersections))
        
        # Endpoints (1 vecino)
        endpoints = (self.skeleton > 0) & (neighbor_count == 1)
        endpoint_coords = np.column_stack(np.where(endpoints))
        
        # Waypoints intermedios (cada 40 píxeles)
        skeleton_points = np.column_stack(np.where(self.skeleton > 0))
        waypoints = skeleton_points[::40]
        
        # Combinar todos
        all_coords = np.vstack([
            intersection_coords,
            endpoint_coords,
            waypoints
        ])
        
        # Clustering para evitar duplicados
        if len(all_coords) > 0:
            clustering = DBSCAN(eps=15, min_samples=1).fit(all_coords)
            
            nodes = []
            for label in set(clustering.labels_):
                cluster = all_coords[clustering.labels_ == label]
                centroid = cluster.mean(axis=0).astype(int)
                nodes.append(tuple(centroid))
        else:
            nodes = []
        
        print(f"  ✓ Nodos detectados: {len(nodes)}")
        
        # Visualizar
        nodes_img = cv2.cvtColor(self.skeleton, cv2.COLOR_GRAY2BGR)
        for node in nodes:
            cv2.circle(nodes_img, (node[1], node[0]), 4, (0, 0, 255), -1)
        
        cv2.imwrite('output/nodes_from_edited.png', nodes_img)
        
        return nodes
    
    def build_graph(self, nodes):
        """Construir grafo"""
        print(f"\n[4/4] Construyendo grafo...")
        print(f"  Procesando {len(nodes)} nodos...")
        
        graph = {node: [] for node in nodes}
        
        # Dilatar skeleton para ser permisivo
        skeleton_dilated = cv2.dilate(self.skeleton, np.ones((5,5), np.uint8), iterations=2)
        
        connections = 0
        
        for i, node_a in enumerate(nodes):
            if i % 20 == 0:
                print(f"  Progreso: {i}/{len(nodes)}")
            
            for node_b in nodes[i+1:]:
                distance = np.linalg.norm(np.array(node_a) - np.array(node_b))
                
                if distance > 80:
                    continue
                
                # Line tracing
                line = np.zeros_like(skeleton_dilated)
                cv2.line(line, (node_a[1], node_a[0]), (node_b[1], node_b[0]), 255, 3)
                
                overlap = cv2.bitwise_and(line, skeleton_dilated)
                ratio = np.sum(overlap > 0) / np.sum(line > 0)
                
                if ratio > 0.45:
                    graph[node_a].append((node_b, distance))
                    graph[node_b].append((node_a, distance))
                    connections += 1
        
        self.graph = graph
        print(f"  ✓ Conexiones: {connections}")
        
        # Visualizar
        self._visualize(nodes, graph)
        
        return graph
    
    def _visualize(self, nodes, graph):
        """Visualizar grafo"""
        print("\n[5/4] Generando visualizaciones...")
        
        # Grafo sobre mapa original
        img = self.original_map.copy()
        
        # Conexiones
        for node, neighbors in graph.items():
            for neighbor, dist in neighbors:
                cv2.line(img, (node[1], node[0]), (neighbor[1], neighbor[0]),
                        (0, 255, 0), 2, cv2.LINE_AA)
        
        # Nodos
        for node in nodes:
            num_conn = len(graph[node])
            
            if num_conn >= 4:
                color = (0, 0, 255)
                radius = 6
            elif num_conn >= 2:
                color = (0, 165, 255)
                radius = 5
            else:
                color = (255, 0, 255)
                radius = 4
            
            cv2.circle(img, (node[1], node[0]), radius, color, -1)
            cv2.circle(img, (node[1], node[0]), radius+1, (255, 255, 255), 1)
        
        cv2.imwrite('output/final_navigation_graph.png', img)
        
        # Con grid
        h, w = img.shape[:2]
        for x in range(0, w, 50):
            cv2.line(img, (x, 0), (x, h), (100, 100, 100), 1)
            cv2.putText(img, str(x), (x+2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1)
        for y in range(0, h, 50):
            cv2.line(img, (0, y), (w, y), (100, 100, 100), 1)
            cv2.putText(img, str(y), (2, y+12), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255,255,255), 1)
        
        cv2.imwrite('output/final_navigation_graph_with_grid.png', img)
        print("  ✓ Visualizaciones creadas")
    
    def save(self):
        """Guardar grafo"""
        Path('data/maps').mkdir(parents=True, exist_ok=True)
        
        data = {
            'graph': self.graph,
            'skeleton': self.skeleton,
            'map_shape': self.original_map.shape
        }
        
        with open('data/maps/navigation_graph.pkl', 'wb') as f:
            pickle.dump(data, f)
        
        print("\n✓ Grafo guardado: data/maps/navigation_graph.pkl")
    
    def process(self):
        """Procesar todo"""
        print("="*60)
        print("  PROCESANDO MAPA EDITADO MANUALMENTE")
        print("="*60)
        
        self.load_edited_map()
        self.create_skeleton()
        nodes = self.find_nodes()
        self.build_graph(nodes)
        self.save()
        
        # Stats
        total = len(self.graph)
        edges = sum(len(n) for n in self.graph.values()) // 2
        avg = sum(len(n) for n in self.graph.values()) / total if total > 0 else 0
        
        print("\n" + "="*60)
        print("  ✓ COMPLETADO")
        print("="*60)
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   • Nodos: {total}")
        print(f"   • Conexiones: {edges}")
        print(f"   • Promedio: {avg:.1f} conexiones/nodo")
        print(f"\n📁 ARCHIVOS:")
        print(f"   • output/final_navigation_graph_with_grid.png")
        print(f"   • data/maps/navigation_graph.pkl\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("\nUso: python process_edited_map.py <ruta_al_mapa_editado>")
        print("\nEjemplo: python process_edited_map.py output/map_edited.png\n")
        sys.exit(1)
    
    processor = EditedMapProcessor(sys.argv[1])
    processor.process()