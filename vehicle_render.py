import bpy
import os
import math
import json
import sys
import random
import colorsys

## ------------------------- Set up script directory ------------------------- ##
try:
    script_dir = os.path.dirname(bpy.data.filepath)
    if not script_dir:
        raise ValueError
except:
    script_dir = os.getcwd()

## ------------------------- Config (default values) ------------------------- ##
VEHICLE_DATA_PATH = os.path.join(script_dir, "vehicle_data.json") # Path of the JSON file to read vehicle mesh and texture paths
MESH_PATH = "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/models_X" # Base path of the FBX files
WHEEL_MESH_PATH = os.path.join(MESH_PATH, "WorldItems", "Wheel.FBX")
TEXTURE_PATH = "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media/textures" # Base path of the textures
WHEEL_TEXTURE_PATH = os.path.join(TEXTURE_PATH, "Vehicles", "vehicle_wheel.png")
OUTPUT_PATH = os.path.join(script_dir, "output")
IS_SINGLE = True # True will only render 1 angle
VEHICLES = [] # Assign a list of vehicles to render. Leave empty to render all vehicles.
RENDER_ENGINE = "CYCLES" # BLENDER_EEVEE (quick) or CYCLES (slow)
DIMENSION_X = 800 # Render dimension X
DIMENSION_Y = 800 # Render dimension Y

# ------------------------- CLI Argument Parsing ------------------------- #
def cli_parsing():
    global IS_SINGLE, RENDER_ENGINE, DIMENSION_X, DIMENSION_Y, VEHICLES

    args = sys.argv
    if "--" in args:
        idx = args.index("--")
        custom_args = args[idx + 1:]
    else:
        custom_args = []

    # Override with command-line values
    for arg in custom_args:
        if arg.startswith("is_single="):
            IS_SINGLE = arg.split("=", 1)[1].lower() == "true"
        elif arg.startswith("render_engine="):
            RENDER_ENGINE = arg.split("=", 1)[1]
        elif arg.startswith("dim="):
            val = int(arg.split("=", 1)[1])
            DIMENSION_X = val
            DIMENSION_Y = val
        elif arg.startswith("dim_x="):
            DIMENSION_X = int(arg.split("=", 1)[1])
        elif arg.startswith("dim_y="):
            DIMENSION_Y = int(arg.split("=", 1)[1])
        elif arg.startswith("vehicles="):
            vehicles = arg.split("=", 1)[1]
            VEHICLES.extend(v.strip() for v in vehicles.split(",") if v.strip())

## ------------------------- Scene cleanup ------------------------- ##
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

## ------------------------- Vehicle import ------------------------- ##
def import_model(mesh_rel):
    mesh = os.path.join(MESH_PATH, mesh_rel.replace("/", os.sep))
    
    possible_paths = [mesh + ".FBX", mesh + ".fbx"]
    abs_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not abs_path:
        print(f"Model not found for: {mesh_rel}.fbx")
        return False

    bpy.ops.import_scene.fbx(filepath=abs_path)
    return True

## ------------------------- Wheel placement ------------------------- ##
def attach_wheels(id_type):
    WHEEL_ORIGINS = {
        # "Name": (X, Y, Z, Scale) --scale is relative, based on wheel original size
        "Van": {
            "FrontLeft":  (-1.17,  2.75, -1.13),
            "RearLeft":   (-1.17, -1.68, -1.13),
            "FrontRight": (1.17,  2.75, -1.13),
            "RearRight":  (1.17, -1.68, -1.13),
        },
        "StepVan": {
            "FrontLeft":  (-1.17,  2.46, -1.44),
            "RearLeft":   (-1.17, -1.8, -1.44),
            "FrontRight": (1.17,  2.46, -1.44),
            "RearRight":  (1.17, -1.8, -1.44),
        },
        "PickUp": {
            "FrontLeft":  (-1.04,  2.46, -1.05),
            "RearLeft":   (-1.04, -1.84, -1.05),
            "FrontRight": (1.04,  2.46, -1.05),
            "RearRight":  (1.04, -1.84, -1.05),
        },
        "SmallCar02": {
            "FrontLeft":  (-1.00,  1.87, -1.00),
            "RearLeft":   (-1.00, -2.23, -1.00),
            "FrontRight": (1.00,  1.87, -1.00),
            "RearRight":  (1.00, -2.23, -1.00),
        },
        "CarSmall02": {
            "FrontLeft":  (-1.00,  1.87, -1.00),
            "RearLeft":   (-1.00, -2.23, -1.00),
            "FrontRight": (1.00,  1.87, -1.00),
            "RearRight":  (1.00, -2.23, -1.00),
        },
        "CarSmall": {
            "FrontLeft":  (-0.9,  1.61, -0.75),
            "RearLeft":   (-0.9, -1.82, -0.75),
            "FrontRight": (0.9,  1.61, -0.75),
            "RearRight":  (0.9, -1.82, -0.75),
        },
        "SmallCar": {
            "FrontLeft":  (-0.9,  1.61, -0.75),
            "RearLeft":   (-0.9, -1.82, -0.75),
            "FrontRight": (0.9,  1.61, -0.75),
            "RearRight":  (0.9, -1.82, -0.75),
        },
        "SportsCar": {
            "FrontLeft":  (-0.95,  1.9, -0.75),
            "RearLeft":   (-0.95, -1.82, -0.75),
            "FrontRight": (0.95,  1.9, -0.75),
            "RearRight":  (0.95, -1.82, -0.75),
        },
        "SUV": {
            "FrontLeft":  (-1.23,  2.22, -1.0),
            "RearLeft":   (-1.23, -1.84, -1.0),
            "FrontRight": (1.23,  2.22, -1.0),
            "RearRight":  (1.23, -1.84, -1.0),
        },
        "CarLuxury": {
            "FrontLeft":  (-1.25,  2.14, -0.93),
            "RearLeft":   (-1.25, -2.08, -0.93),
            "FrontRight": (1.25,  2.14, -0.93),
            "RearRight":  (1.25, -2.08, -0.93),
        },
        "ModernCar": {
            "FrontLeft":  (-1.1,  2.30, -0.93),
            "RearLeft":   (-1.1, -1.96, -0.93),
            "FrontRight": (1.1,  2.30, -0.93),
            "RearRight":  (1.1, -1.96, -0.93),
        },
        "OffRoad": {
            "FrontLeft":  (-1.04,  1.93, -0.93),
            "RearLeft":   (-1.04, -1.7, -0.93),
            "FrontRight": (1.04,  1.93, -0.93),
            "RearRight":  (1.04, -1.7, -0.93),
        },
        "Trailer_Horsebox": {
            "FrontLeft":  (-1.31,  -1.23, -1.65, 0.9),
            "RearLeft":   (-1.31, -2.22, -1.65, 0.9),
            "FrontRight": (1.31,  -1.23, -1.65, 0.9),
            "RearRight":  (1.31, -2.23, -1.65, 0.9),
        },
        "Trailer_Livestock": {
            "FrontLeft":  (-1.17,  -0.67, -1.25, 0.9),
            "RearLeft":   (-1.17, -1.66, -1.25, 0.9),
            "FrontRight": (1.17,  -0.67, -1.25, 0.9),
            "RearRight":  (1.17, -1.66, -1.25, 0.9),
        },
        "TrailerAdvert": {
            "FrontLeft":  (-0.8,  0, -1.71, 0.9),
            "RearLeft":   (-0.8, -1, -1.71, 0.9),
            "FrontRight": (0.8,  0, -1.71, 0.9),
            "RearRight":  (0.8, -1, -1.71, 0.9),
        },
        "Trailer": {
            "Left":  (-0.8,  -0.78, -0.45, 0.9),
            "Right": (0.8,  -0.78, -0.45, 0.9),
        },
        # Base.CarNormal
        "default": {
            "FrontLeft":  (-1.04,  2.67, -0.93),
            "RearLeft":   (-1.04, -1.96, -0.93),
            "FrontRight": (1.04,  2.67, -0.93),
            "RearRight":  (1.04, -1.96, -0.93),
        }
    }

    # Skip burnt variants
    if "burnt" in id_type.lower():
        print(f"Skipping wheels for burnt variant: {id_type}")
        return

    # Get origin group
    origin_group = WHEEL_ORIGINS["default"]
    for prefix, origins in WHEEL_ORIGINS.items():
        if prefix != "default" and id_type.startswith(prefix):
            origin_group = origins
            break

    # Load wheel texture
    try:
        wheel_image = bpy.data.images.load(WHEEL_TEXTURE_PATH)
    except:
        print(f"Failed to load wheel texture: {WHEEL_TEXTURE_PATH}")
        wheel_image = None

    # Import wheels
    for wheel_name, position in origin_group.items():
        try:
            bpy.ops.import_scene.fbx(filepath=WHEEL_MESH_PATH)

            for obj in bpy.context.selected_objects:
                if obj.type != "MESH":
                    continue

                x, y, z, *maybe_scale = position
                scale_factor = maybe_scale[0] if maybe_scale else 1.0

                # Multiply original mesh scale
                orig_scale = obj.scale[0]
                final_scale = orig_scale * scale_factor
                obj.scale = (final_scale, final_scale, final_scale)

                obj.location = (x, y, z)
                if "Right" in wheel_name:
                    obj.rotation_euler = (math.radians(-180), math.radians(-90), 0)
                else:
                    obj.rotation_euler = (0, math.radians(-90), 0)
                obj.name = f"{id_type}_{wheel_name}_Wheel"

                if wheel_image:
                    mat = bpy.data.materials.new(name=f"WheelMat_{wheel_name}")
                    mat.use_nodes = True
                    obj.data.materials.clear()
                    obj.data.materials.append(mat)

                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links
                    nodes.clear()

                    tex = nodes.new("ShaderNodeTexImage")
                    tex.image = wheel_image
                    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
                    output = nodes.new("ShaderNodeOutputMaterial")

                    tex.location = (-400, 0)
                    bsdf.location = (0, 0)
                    output.location = (400, 0)

                    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
                    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.shade_smooth()

        except Exception as e:
            print(f"Failed to import or assign {wheel_name} wheel: {e}")

## ------------------------- Texture assignment ------------------------- ##
def generate_vehicle_colour() -> tuple[float, float, float, float]:
    """Mimics game's doVehicleColor() logic in BaseVehicle.class, returning rgba."""
    roll = random.randint(0, 99)

    if roll < 20:
        hue = random.uniform(0.0, 0.03)
        sat = random.uniform(0.85, 1.0)
        val = random.uniform(0.55, 0.85)
    elif roll < 32:
        hue = random.uniform(0.55, 0.61)
        sat = random.uniform(0.85, 1.0)
        val = random.uniform(0.65, 0.75)
    elif roll < 67:
        hue = 0.15
        sat = random.uniform(0.0, 0.1)
        val = random.uniform(0.7, 0.8)
    elif roll < 89:
        hue = random.uniform(0.0, 1.0)
        sat = random.uniform(0.0, 0.1)
        val = random.uniform(0.1, 0.25)
    else:
        hue = random.uniform(0.0, 1.0)
        sat = random.uniform(0.6, 0.75)
        val = random.uniform(0.3, 0.7)

    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return round(r, 4), round(g, 4), round(b, 4), 1.0

def apply_texture(texture_path, id_type):
    image_path = os.path.join(TEXTURE_PATH, texture_path.replace("/", os.sep) + ".png")
    image = bpy.data.images.load(image_path)

    for obj in bpy.context.selected_objects:
        if obj.type != 'MESH':
            continue

        bpy.context.view_layer.objects.active = obj
        if not obj.data.uv_layers:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.uv.smart_project()
            bpy.ops.object.mode_set(mode='OBJECT')

        mat = bpy.data.materials.new(name="AutoMat")
        mat.use_nodes = True
        obj.data.materials.clear()
        obj.data.materials.append(mat)

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        output = nodes.new("ShaderNodeOutputMaterial")

        tex.location = (-400, 0)
        bsdf.location = (0, 0)
        output.location = (400, 0)

        # Create a base colour node (fallback for transparent texture)
        base_color = nodes.new("ShaderNodeRGB")
        vehicle_colour = generate_vehicle_colour()
        print(f"[{id_type}] Generated colour: {vehicle_colour}")
        base_color.outputs[0].default_value = vehicle_colour

        # Mix base colour with texture
        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'MIX'
        mix.inputs['Fac'].default_value = 1.0
        links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
        links.new(base_color.outputs["Color"], mix.inputs[1]) # Base underneath
        links.new(tex.outputs["Color"], mix.inputs[2]) # Texture on top

        # Connect mix output to BSDF
        links.new(mix.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

        bpy.ops.object.shade_smooth()

## ------------------------- Render logic ------------------------- ##
def render_vehicle(id_type, model_rel, texture_rel):
    print(f"Rendering: {id_type}")
    clear_scene()

    try:
        import_model(model_rel)
        apply_texture(texture_rel, id_type)
        attach_wheels(id_type)
    except Exception as e:
        print(f"Failed to import or apply texture: {id_type}\n{e}")
        return
    
    scene = bpy.context.scene

    # Add sun
    if not any(obj.type == 'LIGHT' for obj in scene.objects):
        bpy.ops.object.light_add(type='SUN', location=(5, -5, 5))

    # Render settings
    scene_render = scene.render
    scene_render.resolution_x = DIMENSION_X
    scene_render.resolution_y = DIMENSION_Y
    scene_render.engine = RENDER_ENGINE
    scene_render.image_settings.file_format = 'PNG'
    scene_render.film_transparent = True

    # Camera position
    radius = 12
    height = 2.7
    pitch_deg = 75
    pitch_rad = math.radians(pitch_deg)

    count = 1 if IS_SINGLE else 8

    for i in range(count):
        origin_z = 135
        angle_deg = origin_z + i * 45
        angle_rad = math.radians(angle_deg)

        # Position camera
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        z = height

        bpy.ops.object.camera_add(location=(x, y, z))
        cam = bpy.context.object
        scene.camera = cam
        cam.data.lens = 40

        # Aim camera at origin
        cam.rotation_euler = (pitch_rad, 0, angle_rad - math.radians(-90))

        if i == 0:
            filename = f"{id_type}_Model.png"
        else:
            filename = f"{id_type}_{i}_Model.png"
        render_path = os.path.join(OUTPUT_PATH, filename)
        scene_render.filepath = render_path

        bpy.ops.render.render(write_still=True)
        if IS_SINGLE:
            print(f"[{id_type}] Render saved: {filename}")
        else:
            print(f"[{id_type}] Render {i+1}/{count} saved: {filename}")

## ------------------------- Process vehicles ------------------------- ##
def process_vehicles(vehicles_list=None):
    with open(VEHICLE_DATA_PATH, 'r', encoding='utf-8') as f:
        all_vehicles = json.load(f)

    for vehicle_id, entry in all_vehicles.items():
        id_type = vehicle_id.split(".", 1)[1]
        mesh = entry.get("mesh", "")
        mesh = mesh.split("|", 1)[0]
        texture = entry.get("texture")

        if not mesh or not texture:
            print(f"Missing mesh or texture for {vehicle_id}, skipping.")
            continue

        if vehicles_list and vehicle_id not in vehicles_list:
            continue

        render_vehicle(id_type, mesh, texture)

## ------------------------- Initialise ------------------------- ##
cli_parsing()
process_vehicles(vehicles_list=VEHICLES)
