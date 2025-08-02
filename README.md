
# Intersector

This Python script identifies whether a given 3D geometry from a STEP (`.stp`) file intersects with a specified plane (defined by a point and normal vector).  
If an intersection exists, it:
- creates a new STEP file with the intersection geometry
- saves a PNG image visualizing the original geometry and the plane
- logs OCC library output for debugging

# Features
- Loads and parses STEP files  
- Computes intersection with a plane (point-normal form)  
- Exports intersection geometry to a new STEP file  
- Generates visualization (PNG) of geometry + plane  
- Captures OCC library logs to a file for reproducibility

# Requirements

- Python 3.11+
- [pythonocc-core](https://github.com/tpaviot/pythonocc-core)
- Standard libraries: `os`, `argparse`, `contextlib`, `sys`

Dependencies can be installed via `conda`.  

```bash
conda env create -f environment.yml
```

# Usage

```bash
python intersector.py \
  --in-step path/to/geometry.stp \
  --in-plane x y z nx ny nz \
  [--out-step output_intersection.stp]
```

# Parameters

| Argument     | Type    | Description |
| ------------ | ------: | ----------- |
| `--in-step`  | string  | Path to input STEP (`.stp`) file containing the geometry |
| `--in-plane` | 6 floats| First 3: point on the plane (x, y, z); next 3: normal vector (nx, ny, nz) 
| `--out-step` | string  | Filename for output STEP file with intersection (default: `intersection.stp` in same folder) |


# Example

```bash
python intersection_finder.py \
  --in-step models/part.stp \
  --in-plane 0 0 0 0 0 1 \
  --out-step part_intersection.stp
```

If an intersection is found:
- The file `part_intersection.stp` will contain the intersection geometry.
- A visualization image `part.png` will be saved alongside the input STEP file.
- Detailed logs will be saved in `lib_occ.log` in the same folder.

If no intersection is found, a message is printed and no files are written.

# Output files

- `intersection.stp` (or your custom name): intersection geometry as STEP file
- `inputname.png`: visualization image of geometry and plane
- `lib_occ.log`: OCC library log output

