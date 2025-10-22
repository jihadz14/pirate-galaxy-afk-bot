"""
Map Processor FINAL - Procesamiento mínimo
Trabaja directamente con el threshold, sin operaciones agresivas
"""

import cv2
import numpy as np
from skimage.morphology import skeletonize
from pathlib import Path
import pickle

class MapProcessorFinal:
    def __init__(self, map_image_path):
        self.map_path = Path(map_image_path)
        self.original_map = None
        self.processed_map = None
        self.skeleton = None
        self.graph = None
        
    def load_map(self):
        """Cargar imagen del mapa"""
        self.original_map = cv2.imread(str(self.map_path))
        if self.original_map is None:
            raise FileNotFoundError(f"No se pudo cargar: {self.map_path}")
        print(f"✓ Mapa cargado: {self.original_map.shape}")
        return self.original_map
    
    def extract_paths_minimal(self, debug=True):
        """
        Extracción MÍNIMA - solo threshold y limpieza muy suave
        """
        print("\n[1/5] Extrayendo caminos (procesamiento mínimo)...")
        
        gray = cv2.cvtColor(self.original_map, cv2.COLOR_BGR2GRAY)
        
        # Solo threshold - SIN operaciones morfológicas agresivas
        _, binary = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)
        
        if debug:
            cv2.imwrite('output/paths_extracted.png', binary)
            print("  ✓ Threshold aplicado")
        
        # ÚNICA operación: Limpiar píxeles sueltos MUY suavemente
        kernel = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        if debug:
            cv2.imwrite('output/paths_cleaned.png', binary)
            print("  ✓ Limpieza mínima aplicada")
        
        # Estadísticas
        coverage = (np.sum(binary > 0) / binary.size) * 100
        print(f"  📊 Cobertura: {coverage:.1f}%")
        
        self.processed_map = binary
        return binary
    
    def create_skeleton(self, debug=True):
        """Crear skeleton"""
        print("\n[2/5] Creando skeleton...")
        
        if self.processed_map is None:
            self.extract_paths_minimal(debug=False)
        
        binary_map = (self.processed_map > 0).astype(np.uint8)
        skeleton = skeletonize(binary_map)
        skeleton_img = (skeleton * 255).astype(np.uint8)
        
        self.skeleton = skeleton_img
        
        if debug:
            overlay = self.original_map.copy()
            overlay[skeleton_img > 0] = [0, 255, 0]
            
            cv2.imwrite('output/skeleton.png', skeleton_img)
            cv2.imwrite('output/skeleton_overlay.png', overlay)
            print("  ✓ Skeleton creado")
        
        return skeleton_img
    
    def find_nodes_smart(self, debug=True):
        """
        Detección inteligente de nodos
        - Intersecciones (3+ vecinos)
        - Puntos cada X píxeles del skeleton (waypoints intermedios)
        """
        print("\n[3/5] Detectando nodos...")
        
        if self.skeleton is None:
            self.create_skeleton(debug=False)
        
        # Método 1: Intersecciones clásicas
        kernel = np.ones((3, 3), np.uint8)
        kernel[1, 1] = 0
        neighbor_count = cv2.filter2D(self.skeleton // 255, -1, kernel)
        
        # Nodos principales: 3+ vecinos
        intersections_mask = (self.skeleton > 0) & (neighbor_count >= 3)
        intersection_coords = np.column_stack(np.where(intersections_mask))
        
        # Clustering de intersecciones
        from sklearn.cluster import DBSCAN
        
        nodes = []
        
        if len(intersection_coords) > 0:
            clustering = DBSCAN(eps=10, min_samples=1).fit(intersection_coords)
            for label in set(clustering.labels_):
                cluster = intersection_coords[clustering.labels_ == label]
                centroid = cluster.mean(axis=0).astype(int)
                nodes.append(tuple(centroid))
        
        print(f"  ✓ Intersecciones: {len(nodes)}")
        
        # Método 2: Waypoints a lo largo del skeleton
        # Tomar puntos cada 30 píxeles del skeleton
        skeleton_points = np.column_stack(np.where(self.skeleton > 0))
        
        # Submuestrear waypoints
        waypoints = []
        if len(skeleton_points) > 0:
            # Tomar 1 de cada 30 puntos
            for point in skeleton_points[::30]:
                # Solo agregar si está lejos de intersecciones existentes
                too_close = False
                for node in nodes:
                    dist = np.linalg.norm(np.array(point) - np.array(node))
                    if dist < 20:
                        too_close = True
                        break
                
                if not too_close:
                    waypoints.append(tuple(point))
        
        print(f"  ✓ Waypoints intermedios: {len(waypoints)}")
        
        # Combinar ambos tipos de nodos
        all_nodes = nodes + waypoints
        print(f"  ✓ Total de nodos: {len(all_nodes)}")
        
        if debug:
            nodes_img = cv2.cvtColor(self.skeleton, cv2.COLOR_GRAY2BGR)
            
            # Intersecciones en rojo
            for node in nodes:
                cv2.circle(nodes_img, (node[1], node[0]), 5, (0, 0, 255), -1)
            
            # Waypoints en azul
            for waypoint in waypoints:
                cv2.circle(nodes_img, (waypoint[1], waypoint[0]), 3, (255, 0, 0), -1)
            
            cv2.imwrite('output/nodes_detected.png', nodes_img)
            print("  ✓ Nodos visualizados")
        
        return all_nodes
    
    def build_graph_permissive(self, nodes, debug=True):
        """
        Grafo con detección MUY permisiva de conexiones
        """
        print(f"\n[4/5] Construyendo grafo de navegación...")
        print(f"  Procesando {len(nodes)} nodos...")
        
        if self.skeleton is None:
            self.create_skeleton(debug=False)
        
        graph = {node: [] for node in nodes}
        
        # Dilatar skeleton para ser MÁS permisivo
        kernel = np.ones((5, 5), np.uint8)
        skeleton_dilated = cv2.dilate(self.skeleton, kernel, iterations=2)
        
        connections = 0
        total_pairs = len(nodes) * (len(nodes) - 1) // 2
        
        print(f"  Analizando {total_pairs} posibles conexiones...")
        
        checked = 0
        for i, node_a in enumerate(nodes):
            if i % 20 == 0 and i > 0:
                print(f"  Progreso: {i}/{len(nodes)} nodos procesados...")
            
            for node_b in nodes[i+1:]:
                checked += 1
                
                distance = np.linalg.norm(np.array(node_a) - np.array(node_b))
                
                # Distancia máxima muy generosa
                if distance > 100:
                    continue
                
                # Line tracing MUY permisivo
                line_img = np.zeros_like(skeleton_dilated)
                cv2.line(line_img, (node_a[1], node_a[0]), (node_b[1], node_b[0]), 255, 3)
                
                intersection = cv2.bitwise_and(line_img, skeleton_dilated)
                overlap_ratio = np.sum(intersection > 0) / np.sum(line_img > 0)
                
                # MUY permisivo: solo 40% overlap necesario
                if overlap_ratio > 0.40:
                    graph[node_a].append((node_b, distance))
                    graph[node_b].append((node_a, distance))
                    connections += 1
        
        self.graph = graph
        
        print(f"  ✓ Conexiones creadas: {connections}")
        
        # Estadísticas
        isolated_nodes = sum(1 for neighbors in graph.values() if len(neighbors) == 0)
        if isolated_nodes > 0:
            print(f"  ⚠ Nodos aislados (sin conexiones): {isolated_nodes}")
        
        if debug:
            self._visualize_graph(nodes, graph)
        
        return graph
    
    def _visualize_graph(self, nodes, graph):
        """Visualización del grafo"""
        print("\n[5/5] Generando visualizaciones...")
        
        # Imagen del grafo
        graph_img = self.original_map.copy()
        
        # Dibujar conexiones primero (abajo)
        for node, neighbors in graph.items():
            for neighbor, distance in neighbors:
                y1, x1 = node
                y2, x2 = neighbor
                
                # Color según distancia
                color_intensity = min(180, int(distance * 2))
                color = (0, 255 - color_intensity, color_intensity)
                cv2.line(graph_img, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
        
        # Dibujar nodos encima
        for node in nodes:
            y, x = node
            num_connections = len(graph[node])
            
            if num_connections == 0:
                color = (128, 128, 128)  # Gris - aislado
                radius = 3
            elif num_connections >= 4:
                color = (0, 0, 255)  # Rojo - intersección importante
                radius = 6
            elif num_connections >= 2:
                color = (0, 165, 255)  # Naranja
                radius = 5
            else:
                color = (255, 0, 255)  # Magenta
                radius = 4
            
            cv2.circle(graph_img, (x, y), radius, color, -1)
            cv2.circle(graph_img, (x, y), radius+1, (255, 255, 255), 1)
        
        cv2.imwrite('output/navigation_graph.png', graph_img)
        print("  ✓ Grafo guardado")
        
        # Versión con grid de coordenadas
        grid_img = graph_img.copy()
        height, width = grid_img.shape[:2]
        
        # Grid cada 50px
        for x in range(0, width, 50):
            cv2.line(grid_img, (x, 0), (x, height), (80, 80, 80), 1)
            cv2.putText(grid_img, str(x), (x+3, 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
        
        for y in range(0, height, 50):
            cv2.line(grid_img, (0, y), (width, y), (80, 80, 80), 1)
            cv2.putText(grid_img, str(y), (3, y+12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1, cv2.LINE_AA)
        
        cv2.imwrite('output/navigation_graph_with_grid.png', grid_img)
        print("  ✓ Grafo con grid guardado")
        
        # Leyenda
        legend = np.zeros((150, 300, 3), dtype=np.uint8)
        legend[:] = (30, 30, 30)
        
        cv2.putText(legend, "LEYENDA DE NODOS:", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        colors = [
            ((0, 0, 255), "Rojo: Interseccion (4+ conexiones)"),
            ((0, 165, 255), "Naranja: Nodo (2-3 conexiones)"),
            ((255, 0, 255), "Magenta: Waypoint (1 conexion)"),
            ((128, 128, 128), "Gris: Nodo aislado (0 conexiones)")
        ]
        
        y_pos = 55
        for color, text in colors:
            cv2.circle(legend, (20, y_pos), 5, color, -1)
            cv2.putText(legend, text, (35, y_pos+5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            y_pos += 25
        
        cv2.imwrite('output/legend.png', legend)
    
    def save_graph(self, output_path='data/maps/navigation_graph.pkl'):
        """Guardar grafo"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'graph': self.graph,
            'skeleton': self.skeleton,
            'map_shape': self.original_map.shape
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"\n✓ Grafo guardado: {output_path}")
    
    def process_all(self):
        """Pipeline completo"""
        print("\n" + "="*70)
        print("  MAP PROCESSOR FINAL - Procesamiento Mínimo")
        print("="*70)
        
        self.load_map()
        self.extract_paths_minimal()
        self.create_skeleton()
        nodes = self.find_nodes_smart()
        self.build_graph_permissive(nodes)
        self.save_graph()
        
        # Estadísticas finales
        total_nodes = len(self.graph)
        total_edges = sum(len(n) for n in self.graph.values()) // 2
        
        if total_nodes > 0:
            avg_connections = sum(len(n) for n in self.graph.values()) / total_nodes
            isolated = sum(1 for n in self.graph.values() if len(n) == 0)
        else:
            avg_connections = 0
            isolated = 0
        
        print("\n" + "="*70)
        print("  ✓ PROCESAMIENTO COMPLETADO")
        print("="*70)
        print(f"\n📊 ESTADÍSTICAS DEL GRAFO:")
        print(f"   • Nodos totales: {total_nodes}")
        print(f"   • Conexiones: {total_edges}")
        print(f"   • Promedio conexiones/nodo: {avg_connections:.1f}")
        print(f"   • Nodos aislados: {isolated}")
        
        print(f"\n📁 ARCHIVOS GENERADOS:")
        print(f"   • output/paths_cleaned.png - Caminos procesados")
        print(f"   • output/skeleton_overlay.png - Skeleton sobre mapa")
        print(f"   • output/nodes_detected.png - Nodos detectados")
        print(f"   • output/navigation_graph.png - Grafo completo")
        print(f"   • output/navigation_graph_with_grid.png - Con coordenadas")
        print(f"   • output/legend.png - Leyenda de colores")
        print(f"   • data/maps/navigation_graph.pkl - Datos para el bot")
        
        print(f"\n🎯 SIGUIENTE PASO:")
        print(f"   Revisa 'navigation_graph_with_grid.png' para elegir waypoints")
        print(f"   Usa las coordenadas del grid para definir rutas de patrulla\n")


if __name__ == '__main__':
    Path('output').mkdir(exist_ok=True)
    
    processor = MapProcessorFinal('data/maps/mantis_hive_map.png')
    processor.process_all()