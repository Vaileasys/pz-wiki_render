# PZwiki Render Script
This script automates rendering Project Zomboid models using Blender.

## Requirements
- [Blender](https://www.blender.org/) (tested with **4.0**)
- Project Zomboid installation

### Vehicles
- `vehicle_data.json` file containing vehicle mesh and texture paths. (A version is packaged with the script)
   - Obtained from [pz-wiki_parser](https://github.com/Vaileasys/pz-wiki_parser)
   - Tools > Vehicle render data
- Convert FBX files from ASCII format to binary. **[FBX Converter 2013](https://aps.autodesk.com/developer/overview/fbx-converter-archives)** can be used ([mirror](https://archive.org/details/fbx20133_converter_win_x64))

### Items
- `model_data.json` file containing model mesh and textre paths. (A version is packaged with the script)
   - Obtained from [pz-wiki_parser](https://github.com/Vaileasys/pz-wiki_parser)
   - Script parser > model

---

## Usage in Blender (Scripting: Text Eeditor)
1. Open Blender.
2. Paste the `vehicle_render.py` or `model_render.py` script into the **Text Editor** in **Scripting**.
3. Adjust settings in the config section if needed:
   - `MEDIA_PATH` - should be the path of the media file in the Project Zomboid directory.
   - `MODEL_DATA_PATH` - should be the path of the JSON data file.
   - `OUTPUT_PATH` - where rendered images will be saved (default: `./output`).
   - `IS_SINGLE = True` - render a single angle. `False` will render each vehicle from 8 different angles.
   - `MODELS = ["Base.CarLuxury"]` - only render selected models.
4. Click **Run Script** (the play button in the Text Editor toolbar).

Note: Config (default values) can be modified as needed.

## Usage from Command Line
Run Blender in background by using:

`blender --background --python vehicle_render.py`

Or:

`blender --background --python model_render.py`

### Available CLI Arguments
Arguments can be defined by adding them after `--`

- `is_single=true` (Boolean) - If true, renders one angle instead of eight (default)
- `render_engine=` (String) - `BLENDER_EEVEE` (quick) or `CYCLES` (slow)
- `dim=800` (Integer) - Sets render dimension of both width and height. `dim_x` and `dim_y` can used to define separately.

#### Vehicles
- `vehicles` (List) - List each vehicle ID, separating with a comma (`,`).

Example:

`blender --background --python vehicle_render.py -- is_single=true render_engine=BLENDER_EEVEE dim=800 vehicles=Base.CarNormal,Base.Van`

#### Models
- `models` (List) - List each vehicle ID, separating with a comma (`,`).
- `lens` (Integer) - Focal length to be used for the render.
- `cam` (Integer) - Camera index with 45° intervals. (0 to 7)
- `preset` (String) - Option preset with differing `FOCAL_LENGTH` and `CAM_INDEX`.
   - Presets are broken up into 2 parts. `<lens>-<cam>`
   - `<lens>` - the focal length and can be any of the following: `huge` (200), `large` (400), `med` (600), `small` (1000), `tiny` (1600)
   - `<cam>` - the camera index to use, in intervals of 2: `0` (0), `1` (2), `2` (4), `3` (6)

Example:

`blender --background --python model_render.py -- preset=med-1 models=BeerBottleSixpack`

### Notes
- Ensure Blender is added to your system PATH
- Alternatively, include the Blender executable path in the command:
`& "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" --background --python vehicle_render.py`

---

## Output
Rendered images are saved to the `output/` folder beside the script (default). Ensure the full path is defined if running in Blender: Scripting.

Filenames follow the format:
- `CarLuxury_Model.png` - single angle
- `CarLuxury_Model.png`, ..., `CarLuxury_7_Model.png` - full rotation

---

## Note
- Rendering all models at once will take a while. Be patient. If rendering in Blender it may indicate that it's stopped responding.
- There are several bathfiles with varying settings. These can be used to simplify using in the CLI.