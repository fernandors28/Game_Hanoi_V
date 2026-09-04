
import os
import pyvista as pv


class Disco_Scene:
    def __init__(self):
        self.colores = [
            "#04A373",  # Disco 1 (Grande - Verde)
            "#EB3946",  # Disco 2 (Mediano - Rojo)
            "#457590",  # Disco 3 (Pequeño - Azul)
        ]

    def cargar_disco(self, numero):
        archivo = f"disco_{numero}.stl"
        if not os.path.exists(archivo):
            print(f"❌ Archivo no encontrado: {archivo}")
            return None
        return pv.read(archivo)

    def apilar_tres_discos(self, plotter, x_poste, z_sup=0.2):
        diccionario_discos = {}
        poste_izquierdo = []
        z_acumulado = z_sup

        for i in range(3):
            malla = self.cargar_disco(i + 1)
            if malla is None:
                continue

            malla_pos = malla.copy()

            # 1. Obtener los límites del modelo original
            min_x, max_x, min_y, max_y, min_z, max_z = malla_pos.bounds
            centro_x = (min_x + max_x) / 2
            centro_y = (min_y + max_y) / 2
            altura_disco = max_z - min_z

            # 2. Vector de desplazamiento exacto hacia la coordenada de destino
            dx = x_poste - centro_x
            dy = 0.0 - centro_y
            dz = z_acumulado - min_z
            
            # 3. Mover la malla en un solo paso
            malla_pos.translate((dx, dy, dz), inplace=True)

            # 4. Renderizar en la escena
            actor = plotter.add_mesh(
                malla_pos,
                color=self.colores[i],
                smooth_shading=True,
                show_edges=True,
                edge_color=(0.1, 0.08, 0.05),
                line_width=1.2,
            )

            diccionario_discos[i] = {"malla": malla_pos, "actor": actor}
            poste_izquierdo.append(i)

            # Acumular la altura para apilar el siguiente disco justo encima
            z_acumulado += altura_disco

        pegs = [poste_izquierdo, [], []]
        return diccionario_discos, pegs