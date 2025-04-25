import bpy
import os
import math
import json
import sys
import addon_utils
from mathutils import Vector

# Enable Import X add-on
#addon_utils.enable("io_import_x-master", default_set=True)
# --Commented so it skips, as these models are not currently selected in the imported models logic

## ------------------------- Set up script directory ------------------------- ##
try:
    script_dir = os.path.dirname(bpy.data.filepath)
    if not script_dir:
        raise ValueError
except:
    script_dir = os.getcwd()

## ------------------------- Config (default values) ------------------------- ##

# ---- Config: File paths ---- #
MEDIA_PATH = "C:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/media" # Path to the game's 'media' directory
MODEL_DATA_PATH = os.path.join(script_dir, "model_data.json") # Path of the JSON file to read model mesh and texture paths
MESH_PATH = os.path.join(MEDIA_PATH, "models_X") # Base path of the FBX files
TEXTURE_PATH = os.path.join(MEDIA_PATH, "textures") # Base path of the textures
OUTPUT_PATH = os.path.join(script_dir, "output")

# ---- Config: Variables ---- #
IS_SINGLE = True # True will only render 1 angle
MODELS = [] # Assign a list of models to render. Leave empty to render all models.
RENDER_ENGINE = "BLENDER_EEVEE" # BLENDER_EEVEE (fast) or CYCLES (slow)
DIMENSION_X = 400 # Render dimension X
DIMENSION_Y = 400 # Render dimension Y
FOCAL_LENGTH = 600
CAM_INDEX = 0

# ---- Config: CLI Presets ---- #
PRESETS = {
    "huge-0": {"focal_length": 200, "cam_index": 0},
    "huge-1": {"focal_length": 200, "cam_index": 2},
    "huge-2": {"focal_length": 200, "cam_index": 4},
    "huge-3": {"focal_length": 200, "cam_index": 6},
    "large-0": {"focal_length": 400, "cam_index": 0},
    "large-1": {"focal_length": 400, "cam_index": 2},
    "large-2": {"focal_length": 400, "cam_index": 4},
    "large-3": {"focal_length": 400, "cam_index": 6},
    "med-0": {"focal_length": 600, "cam_index": 0},
    "med-1": {"focal_length": 600, "cam_index": 2},
    "med-2": {"focal_length": 600, "cam_index": 4},
    "med-3": {"focal_length": 600, "cam_index": 6},
    "small-0": {"focal_length": 1000, "cam_index": 0},
    "small-1": {"focal_length": 1000, "cam_index": 2},
    "small-2": {"focal_length": 1000, "cam_index": 4},
    "small-3": {"focal_length": 1000, "cam_index": 6},
    "tiny-0": {"focal_length": 1600, "cam_index": 0},
    "tiny-1": {"focal_length": 1600, "cam_index": 2},
    "tiny-2": {"focal_length": 1600, "cam_index": 4},
    "tiny-3": {"focal_length": 1600, "cam_index": 6},
}

# ------------------------- CLI Argument Parsing ------------------------- #
def cli_parsing():
    global IS_SINGLE, RENDER_ENGINE, DIMENSION_X, DIMENSION_Y, FOCAL_LENGTH, CAM_INDEX, MODELS, PRESET
    preset = None

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
        elif arg.startswith("preset="):
            preset = arg.split("=", 1)[1]
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
        elif arg.startswith("lens="):
            FOCAL_LENGTH = int(arg.split("=", 1)[1])
        elif arg.startswith("cam="):
            CAM_INDEX = int(arg.split("=", 1)[1])
        elif arg.startswith("models="):
            models = arg.split("=", 1)[1]
            MODELS.extend(v.strip() for v in models.split(",") if v.strip())
    
    # Apply presets
    if preset in PRESETS:
        for key, value in PRESETS[preset].items():
            IS_SINGLE = value if key == "is_single" else IS_SINGLE
            RENDER_ENGINE = value if key == "render_engine" else RENDER_ENGINE
            DIMENSION_X = value if key == "dimension" else DIMENSION_X
            DIMENSION_Y = value if key == "dimension" else DIMENSION_Y
            DIMENSION_X = value if key == "dimension_x" else DIMENSION_X
            DIMENSION_Y = value if key == "dimension_y" else DIMENSION_Y
            FOCAL_LENGTH = value if key == "focal_length" else FOCAL_LENGTH
            CAM_INDEX = value if key == "cam_index" else CAM_INDEX

## ------------------------- Scene cleanup ------------------------- ##
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

## ------------------------- Models import ------------------------- ##
def import_model(mesh_rel, offset_loc=(0, 0, 0), offset_rot=(0, 0, 0)):
    mesh = os.path.join(MESH_PATH, mesh_rel.replace("/", os.sep))

    possible_paths = [mesh + ".FBX", mesh + ".fbx", mesh + ".x", mesh + ".X"]
    abs_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if not abs_path:
        print(f"Model not found for: {mesh_rel}")
        return []

    before_import = set(bpy.context.scene.objects)
    
    ext = os.path.splitext(abs_path)[1].lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=abs_path)
    elif ext == ".x":
        if hasattr(bpy.ops.import_scene, "x"):
            bpy.ops.import_scene.x(filepath=abs_path)
        else:
            print("DirectX importer not available.")

    after_import = set(bpy.context.scene.objects)

    imported_objects = list(after_import - before_import)
    
    for obj in imported_objects:
        # Apply location offset
        obj.location.x += offset_loc[0]
        obj.location.y += offset_loc[1]
        obj.location.z += offset_loc[2]

        # Apply rotation offset (preserve existing orientation)
        obj.rotation_euler.x += math.radians(offset_rot[0])
        obj.rotation_euler.y += math.radians(offset_rot[1])
        obj.rotation_euler.z += math.radians(offset_rot[2])

    return imported_objects

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

        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

#        bpy.ops.object.shade_smooth()

## ------------------------- Render logic ------------------------- ##
def center_object(obj):
    bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_corner = Vector((min(v[i] for v in bbox_world) for i in range(3)))
    max_corner = Vector((max(v[i] for v in bbox_world) for i in range(3)))
    center = (min_corner + max_corner) / 2

    obj.location -= center

def render_model(id_type, model_data):

    mesh_rel = model_data.get("mesh", "")
    mesh_rel = mesh_rel.split("|", 1)[0]
    offset_loc = model_data.get("location", [0, 0, 0])
    offset_rot = model_data.get("rotation", [0, 0, 0])
    is_static = model_data.get("static", True)
    if is_static:
        texture_rel = model_data.get("texture", mesh_rel)
    else:
        texture_rel = "Body/" + model_data.get("texture", model_data.get("animationsMesh", ""))
    camera = model_data.get("camera", {})
    camera_index = camera.get("index", CAM_INDEX)
    camera_lens = camera.get("lens", FOCAL_LENGTH)
    is_static = model_data.get("static", True)

    print(f"Rendering: {id_type}")
    clear_scene()

    try:
        imported_objects = import_model(mesh_rel, offset_loc, offset_rot)

        # Center each mesh at origin
        for obj in imported_objects:
            if obj.type == "MESH":
                center_object(obj)

        # Select for texture
        for obj in bpy.data.objects:
            obj.select_set(False)
        for obj in imported_objects:
            if obj.type == 'MESH':
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj

        apply_texture(texture_rel, id_type)

    except Exception as e:
        print(f"Failed to import or apply texture: {id_type}\n{e}")
        return
    
    scene = bpy.context.scene

    # Add sun
    if not any(obj.type == 'LIGHT' for obj in scene.objects):
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
        sun = bpy.context.object
        sun.data.energy = 2.0

    # Render settings
    scene_render = scene.render
    scene_render.resolution_x = DIMENSION_X
    scene_render.resolution_y = DIMENSION_Y
    scene_render.engine = RENDER_ENGINE
    scene_render.image_settings.file_format = 'PNG'
    scene_render.film_transparent = True

    # Camera position
    radius = 12
    height = 3.215
    pitch_deg = 75
    pitch_rad = math.radians(pitch_deg)

    count = 1 if IS_SINGLE else 8

    for i in range(count):
        origin_z = 135
        angle_deg = origin_z + (camera_index + i) * 45
        angle_rad = math.radians(angle_deg)

        # Position camera (orbiting around 0,0,0)
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        z = height

        bpy.ops.object.camera_add(location=(x, y, z))
        cam = bpy.context.object
        scene.camera = cam
        cam.data.lens = camera_lens

        # Aim camera at origin (consistent stylised angle)
        cam.rotation_euler = (pitch_rad, 0, angle_rad - math.radians(-90))
        sun.rotation_euler = (math.radians(45), 0, angle_rad - math.radians(-90))

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
def process_vehicles(model_list=None):
    with open(MODEL_DATA_PATH, 'r', encoding='utf-8') as f:
        all_models = json.load(f)

    for model_id, model_data in all_models.items():
        id_type = model_id

        if model_list and model_id not in model_list:
            continue

        if not model_data.get("mesh"):
            print(f"Missing mesh for {model_id}, skipping.")
            continue

        render_model(id_type, model_data)

## ------------------------- Initialise ------------------------- ##
cli_parsing()
process_vehicles(model_list=MODELS)