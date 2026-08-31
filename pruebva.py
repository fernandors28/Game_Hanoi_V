import cadquery as cq
def generar_torre_hanoi():
    print("Generando modelos 3D...")

    # ==========================================
    # 1. BASE CON LOS POSTES
    # ==========================================
    # Creamos una caja de 200x60x10.
    base = cq.Workplane("XY").box(200, 60, 10)
    
    # Seleccionamos la cara superior (>Z), ubicamos 3 puntos y extruimos los postes
    base = (
        base.faces(">Z")
        .workplane()
        .pushPoints([(-65, 0), (0, 0), (65, 0)]) # Posición de los 3 postes
        .circle(4)                               # Radio del poste: 4mm
        .extrude(70)                             # Altura del poste: 70mm
    )
    
    cq.exporters.export(base, "base_hanoi.stl")
    print("- Exportado: base_hanoi.stl")

    # ==========================================
    # 2. FUNCIÓN PARA GENERAR DISCOS
    # ==========================================
    def crear_disco(radio_exterior, nombre_archivo):
        disco = (
            cq.Workplane("XY")
            .circle(radio_exterior)
            .extrude(10) # Altura del disco: 10mm
            .faces(">Z")
            .workplane()
            .hole(9) # hole() recibe diámetro. 9mm deja 4.5mm de radio (0.5mm de holgura)
        )
        cq.exporters.export(disco, nombre_archivo)
        print(f"- Exportado: {nombre_archivo}")

    # ==========================================
    # 3. CREAR LOS TRES DISCOS
    # ==========================================
    crear_disco(25, "disco_1_grande.stl")
    crear_disco(20, "disco_2_mediano.stl")
    crear_disco(15, "disco_3_pequeno.stl")
    
    print("¡Proceso completado!")

if __name__ == "__main__":
    generar_torre_hanoi()