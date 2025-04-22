# PZwiki Render Script
This script automates rendering Project Zomboid vehicle models using Blender.

## Requirements
- [Blender](https://www.blender.org/) (tested with **4.0**)
- Project Zomboid installation
- `vehicle_data.json` file containing vehicle mesh and texture paths. (A version is packaged with the script)
   - Obtained from [pz-wiki_parser](https://github.com/Vaileasys/pz-wiki_parser)
   - Tools > Vehicle render data
- Convert FBX files from ASCII format to binary. **[FBX Converter 2013](https://aps.autodesk.com/developer/overview/fbx-converter-archives)** can be used ([mirror](https://archive.org/details/fbx20133_converter_win_x64))

---

## Usage in Blender (Text Editor)
1. Open Blender.
2. Paste the `vehicle_render.py` script into the **Text Editor** in **Scripting**.
3. Adjust settings in the config section if needed:
   - `IS_SINGLE = True` - render a single angle. `False` will render each vehicle from 8 different angles.
   - `VEHICLES = ["Base.CarLuxury"]` - only render selected vehicles.
   - `OUTPUT_PATH` - where rendered images will be saved (default: `./output`).
4. Click **Run Script** (the play button in the Text Editor toolbar).

Note: Config (default values) can be modified as needed.

## Usage from Command Line
Run Blender in background by using:

`blender --background --python vehicle_render.py`

### Available CLI Arguments
Arguments can be defined by adding them after `--`

- `is_single=true` (Boolean) - If true, renders one angle instead of eight (default)
- `render_engine=` (String) - `BLENDER_EEVEE` (quick) or `CYCLES` (slow)
- `dim=800` (Integer) - Sets render dimension of both width and height. `dim_x` and `dim_y` can used to define separately.
- `vehicles` (List) - List each vehicle ID, separating with a comma (`,`).

`blender --background --python vehicle_render.py -- is_single=true render_engine=BLENDER_EEVEE dim=800 vehicles=Base.CarNormal,Base.Van`

### Notes
- Ensure Blender is added to your system PATH
- Alternatively, include the Blender executable path in the command:
`& "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" --background --python vehicle_render.py`

---

## Output
Rendered images are saved to the `output/` folder beside the script (default).  

Filenames follow the format:
- `CarLuxury_Model.png` - single angle
- `CarLuxury_Model.png`, ..., `CarLuxury_7_Model.png` - full rotation

---

## Note
- Rendering all vehicles at once will take a while. Be patient. Blender may indicate that it's stopped responding.