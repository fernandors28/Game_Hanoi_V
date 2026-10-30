from PyQt6.QtCore import Qt, QTimer
import pyvista as pv
import vtk

from camera_Game import ControlGesto
from disco_hanoi import Disco_Scene


class HanoiScene:
    def __init__(self, potter):
        self.potter = potter
        self._drag_disk_idx = None
        self._drag_source_peg = None
        self._drag_origin = None
        self._last_drag_position = None
        self._move_history = []
        self._history_index = 0
        self._hand_target = None
        self._cursor_position = None
        self._hand_grabbing = False
        self._hand_drag_offset = None
        self.Model_Change()
        self._setup_hand_cursor()
    
    def Model_Change(self):
        self.potter.clear()
        self.potter.set_background("white")
        try:
            self.base_mesh = pv.read("base_hanoi.stl")
            xmin, xmax, ymin, ymax, zmin, zmax = self.base_mesh.bounds
            # La base generada mide 10 mm de grosor; zmax incluye la punta de los postes.
            self.base_top_z = zmin + 10.0
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
        self.peg_x_positions = [x_post_izq, 0.0, -x_post_izq]
        self.disk, self.pegs = Disco_Scene().apilar_tres_discos(
            self.potter, x_poste=x_post_izq, z_sup=self.base_top_z
        )
        self.potter.enable_parallel_projection()
        
        # 2. Vista frontal (ajusta a view_xy() si tu STL está orientado diferente)
        self.potter.view_xz()
        
        # 3. Elevar la cámara para ver la parte superior de la base
        self.potter.camera.elevation = 25  # Puedes probar valores entre 10 y 25
        self.potter.add_axes()
        # 4. Ajustar el zoom al contenido
        self.potter.reset_camera()

        self._original_mouse_press = self.potter.mousePressEvent
        self._original_mouse_move = self.potter.mouseMoveEvent
        self._original_mouse_release = self.potter.mouseReleaseEvent
        self.potter.mousePressEvent = self._on_mouse_press
        self.potter.mouseMoveEvent = self._on_mouse_move
        self.potter.mouseReleaseEvent = self._on_mouse_release

    def _setup_hand_cursor(self):
        xmin, xmax, ymin, ymax, zmin, zmax = self.base_mesh.bounds
        margen_x = (xmax - xmin) * 0.25
        altura_poste = zmax - self.base_top_z
        self.gestos = ControlGesto(
            x_min_3d=xmin - margen_x,
            x_max_3d=xmax + margen_x,
            z_min_3d=self.base_top_z - altura_poste * 0.15,
            z_max_3d=zmax + altura_poste * 0.25,
        )
        self.gestos.event_mano.connect(self._set_hand_target)

        cursor_mesh = pv.Sphere(radius=2.2, theta_resolution=20, phi_resolution=20)
        self.hand_cursor_actor = self.potter.add_mesh(
            cursor_mesh,
            color="#00C8FF",
            lighting=False,
            name="hand_cursor",
        )
        self.hand_cursor_actor.SetVisibility(False)
        self.potter.camera.parallel_scale *= 1.05

        self._cursor_timer = QTimer(self.potter)
        self._cursor_timer.setInterval(16)
        self._cursor_timer.timeout.connect(self._animate_hand_cursor)
        self._cursor_timer.start()
        self.gestos.start(fps=30)

    def _set_hand_target(self, x_3d, z_3d, agarrado):
        cursor_y = self.base_mesh.bounds[2] - 3.0
        self._hand_target = (x_3d, cursor_y, z_3d)
        was_grabbing = self._hand_grabbing
        self._hand_grabbing = bool(agarrado)
        if self._cursor_position is None:
            self._cursor_position = self._hand_target
            self.hand_cursor_actor.SetPosition(*self._cursor_position)
        cursor_color = (1.0, 0.55, 0.0) if agarrado else (0.0, 0.78, 1.0)
        self.hand_cursor_actor.GetProperty().SetColor(*cursor_color)
        self.hand_cursor_actor.SetVisibility(True)

        if self._hand_grabbing and not was_grabbing:
            self._cursor_position = self._hand_target
            self.hand_cursor_actor.SetPosition(*self._cursor_position)
            self._begin_hand_drag(x_3d, cursor_y, z_3d)
        elif was_grabbing and not self._hand_grabbing and self._drag_disk_idx is not None:
            self._finish_drag()

    def _animate_hand_cursor(self):
        if self._hand_target is None or self._cursor_position is None:
            return

        smoothing = 0.22
        self._cursor_position = tuple(
            current + (target - current) * smoothing
            for current, target in zip(self._cursor_position, self._hand_target)
        )
        if sum(
            (target - current) ** 2
            for current, target in zip(self._cursor_position, self._hand_target)
        ) < 0.01:
            self._cursor_position = self._hand_target

        self.hand_cursor_actor.SetPosition(*self._cursor_position)
        if self._hand_grabbing and self._drag_disk_idx is not None:
            self._move_hand_drag(self._cursor_position[0], self._cursor_position[2])
        self.potter.render()

    def _event_display_position(self, event):
        position = event.position()
        renderer = self.potter.renderer
        render_width, render_height = renderer.GetSize()
        scale_x = render_width / max(self.potter.width(), 1)
        scale_y = render_height / max(self.potter.height(), 1)
        x = round(position.x() * scale_x)
        y = render_height - round(position.y() * scale_y)
        return x, y

    def _world_position_on_drag_plane(self, display_x, display_y):
        renderer = self.potter.renderer
        world_points = []
        for depth in (0.0, 1.0):
            renderer.SetDisplayPoint(display_x, display_y, depth)
            renderer.DisplayToWorld()
            point = renderer.GetWorldPoint()
            world_points.append(tuple(value / point[3] for value in point[:3]))

        near, far = world_points
        direction_y = far[1] - near[1]
        if abs(direction_y) < 1e-9:
            return None
        amount = -near[1] / direction_y
        return (
            near[0] + amount * (far[0] - near[0]),
            near[2] + amount * (far[2] - near[2]),
        )

    def _begin_hand_drag(self, x_3d, y_3d, z_3d):
        renderer = self.potter.renderer
        renderer.SetWorldPoint(x_3d, y_3d, z_3d, 1.0)
        renderer.WorldToDisplay()
        display_x, display_y, _ = renderer.GetDisplayPoint()
        if self._begin_drag_at_display(round(display_x), round(display_y)):
            center_x, _, center_z = self.disk[self._drag_disk_idx]["malla"].center
            self._hand_drag_offset = (center_x - x_3d, center_z - z_3d)

    def _begin_drag_at_display(self, x, y):
        picker = vtk.vtkCellPicker()
        picker.SetTolerance(0.01)
        picker.InitializePickList()
        for info in self.disk.values():
            picker.AddPickList(info["actor"])
        picker.PickFromListOn()
        if not picker.Pick(x, y, 0, self.potter.renderer):
            return False

        actor = picker.GetActor()
        disk_idx = next(
            (idx for idx, info in self.disk.items() if info["actor"] == actor),
            None,
        )
        source_peg = next(
            (peg_idx for peg_idx, stack in enumerate(self.pegs)
             if stack and stack[-1] == disk_idx),
            None,
        )
        if disk_idx is None or source_peg is None:
            return False

        self._drag_disk_idx = disk_idx
        self._drag_source_peg = source_peg
        self._drag_origin = self.disk[disk_idx]["malla"].center
        self._last_drag_position = self._world_position_on_drag_plane(x, y)
        return True

    def _move_hand_drag(self, x_3d, z_3d):
        if self._hand_drag_offset is None:
            return
        mesh = self.disk[self._drag_disk_idx]["malla"]
        center_x, _, center_z = mesh.center
        target_x = x_3d + self._hand_drag_offset[0]
        target_z = z_3d + self._hand_drag_offset[1]
        mesh.translate((target_x - center_x, 0.0, target_z - center_z), inplace=True)

    def _on_mouse_press(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            self._original_mouse_press(event)
            return

        x, y = self._event_display_position(event)
        if not self._begin_drag_at_display(x, y):
            self._original_mouse_press(event)
            return

    def _on_mouse_move(self, event):
        if self._drag_disk_idx is None:
            self._original_mouse_move(event)
            return

        x, y = self._event_display_position(event)
        current_position = self._world_position_on_drag_plane(x, y)
        if current_position is None or self._last_drag_position is None:
            return

        dx = current_position[0] - self._last_drag_position[0]
        dz = current_position[1] - self._last_drag_position[1]
        self.disk[self._drag_disk_idx]["malla"].translate((dx, 0.0, dz), inplace=True)
        self._last_drag_position = current_position
        self.potter.render()

    def _on_mouse_release(self, event):
        if self._drag_disk_idx is None:
            self._original_mouse_release(event)
            return

        self._finish_drag()

    def _finish_drag(self):
        if self._drag_disk_idx is None:
            return

        disk_idx = self._drag_disk_idx
        source_peg = self._drag_source_peg
        mesh = self.disk[disk_idx]["malla"]
        destination_peg = min(
            range(len(self.peg_x_positions)),
            key=lambda idx: abs(mesh.center[0] - self.peg_x_positions[idx]),
        )
        destination_stack = self.pegs[destination_peg]
        can_place = (
            destination_peg == source_peg
            or self._can_place_disk_on_peg(disk_idx, destination_stack)
        )

        if can_place:
            if destination_peg != source_peg:
                self.pegs[source_peg].pop()
                destination_stack.append(disk_idx)
                del self._move_history[self._history_index:]
                self._move_history.append((disk_idx, source_peg, destination_peg))
                self._history_index = len(self._move_history)
            self._place_disk_on_peg(disk_idx, destination_peg)
        else:
            center_x, center_y, center_z = mesh.center
            origin_x, origin_y, origin_z = self._drag_origin
            mesh.translate(
                (origin_x - center_x, origin_y - center_y, origin_z - center_z),
                inplace=True,
            )

        self._drag_disk_idx = None
        self._drag_source_peg = None
        self._drag_origin = None
        self._last_drag_position = None
        self._hand_drag_offset = None
        self.potter.render()

    def _place_disk_on_peg(self, disk_idx, peg_idx):
        mesh = self.disk[disk_idx]["malla"]
        stack = self.pegs[peg_idx]
        bottom_z = self.base_top_z
        for stacked_idx in stack[:-1]:
            stacked_mesh = self.disk[stacked_idx]["malla"]
            bottom_z += stacked_mesh.bounds[5] - stacked_mesh.bounds[4]

        min_x, max_x, min_y, max_y, min_z, _ = mesh.bounds
        mesh.translate(
            (
                self.peg_x_positions[peg_idx] - (min_x + max_x) / 2,
                -((min_y + max_y) / 2),
                bottom_z - min_z,
            ),
            inplace=True,
        )

    @staticmethod
    def _can_place_disk_on_peg(disk_idx, destination_stack):
        # Los índices menores son discos mayores: 0=grande, 1=mediano, 2=pequeño.
        return not destination_stack or destination_stack[-1] < disk_idx

    def undo_move(self):
        if self._history_index == 0:
            return

        disk_idx, source_peg, destination_peg = self._move_history[self._history_index - 1]
        if not self.pegs[destination_peg] or self.pegs[destination_peg][-1] != disk_idx:
            return

        self.pegs[destination_peg].pop()
        self.pegs[source_peg].append(disk_idx)
        self._place_disk_on_peg(disk_idx, source_peg)
        self._history_index -= 1
        self.potter.render()

    def redo_move(self):
        if self._history_index >= len(self._move_history):
            return

        disk_idx, source_peg, destination_peg = self._move_history[self._history_index]
        destination_stack = self.pegs[destination_peg]
        if (
            not self.pegs[source_peg]
            or self.pegs[source_peg][-1] != disk_idx
            or not self._can_place_disk_on_peg(disk_idx, destination_stack)
        ):
            return

        self.pegs[source_peg].pop()
        destination_stack.append(disk_idx)
        self._place_disk_on_peg(disk_idx, destination_peg)
        self._history_index += 1
        self.potter.render()