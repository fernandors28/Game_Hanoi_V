import pyvista as pv

from disco_hanoi import Disco_Scene


class HanoiScene:
    def __init__(self, potter):
        self.potter = potter
        self.disco_agarrado_idx = None
        self.Model_Change()
    
    def Model_Change(self):
        self.potter.clear()
        self.potter.set_background("white")
        try:
            self.base_mesh = pv.read("base_hanoi.stl")
            xmin, xmax, ymin, ymax, zmin, zmax = self.base_mesh.bounds
            self.potter.enable_eye_dome_lighting()  # Mejora el contraste y la profundidad visual

# 2. Agregar la base con sombreado PBR tipo Madera Barnizada/Mate
            self.potter.add_mesh(
                self.base_mesh,
                color="#8B5A2B",        # Tono madera barnizada (marrón cálido)
                pbr=True,               # Renderizado basado en física
                metallic=0.0,           # La madera no refleja como metal
                roughness=0.6,          # Brillo mate suave/barnizado
                diffuse=0.8,            # Difusión equilibrada de la luz
                smooth_shading=True,
                show_edges=False,       # Desactivar aristas para no romper la superficie lisa
            )
            
            print("Modelo base cargado correctamente.")
        except Exception as e:
            print(f"Error al cargar el modelo base: {e}")
        x_post_izq = xmin * 0.65
        z_sup = zmax
        self.disk, self.pegs = Disco_Scene().apilar_tres_discos(self.potter, x_poste=x_post_izq)
        self.potter.enable_parallel_projection()
        
        # 2. Vista frontal (ajusta a view_xy() si tu STL está orientado diferente)
        self.potter.view_xz()
        
        # 3. Elevar la cámara para ver la parte superior de la base
        self.potter.camera.elevation = 25  # Puedes probar valores entre 10 y 25
        self.potter.add_axes()
        # 4. Ajustar el zoom al contenido
        self.potter.reset_camera()

        self.potter.mouseMoveEvent = lambda event: None
        # Desactiva el zoom con la rueda del ratón
        self.potter.wheelEvent = lambda event: None

    def update_position_hand(self,x_3d, z_3d, agarrado):
        if agarrado:
           if self.disco_agarrado_idx is None:
               self.disco_agarrado_idx = self.search_disk(x_3d,z_3d)

            return
    def search_disk(self, x_3d, z_3d):
        if len(self.pegs[0]) > 0:
            disk_top_idx = self.pegs[0][-1]
            return disk_top_idx
        return None