"""

This script identifies whether a given 3D geometry from a STEP (.stp) file
intersects with a specified plane defined by a point and a normal vector.
If an intersection is found, the script saves:
- a new STEP file containing the intersection geometry
- a PNG image visualizing the original geometry and the plane

The script logs detailed OCC library output to a log file for reproducibility.

Usage:
    python intersector.py \
        --in-step path/to/file.stp \
        --in-plane x y z nx ny nz \
        [--out-step output_intersection.stp]

Arguments:
    --in-step   : Path to the input STEP (.stp) file containing the geometry.
    --in-plane  : Six floats: first three (x, y, z) as a point on the plane,
                  next three (nx, ny, nz) as the normal vector of the plane.
    --out-step  : Optional; filename for the intersection STEP file.
                  Defaults to 'intersection.stp' in the same directory.

Outputs:
    - intersection STEP file if intersection exists
    - PNG image visualizing the geometry and plane
    - log file capturing OCC internal output

"""

import os
import argparse
import common_lib
import step_file_lib

##########################################

def main():
    """
    Parses command-line arguments and runs the intersection detection.

    Steps:
    1. Parse the STEP input file and plane definition (point + normal).
    2. Compute intersection of the plane with the geometry.
    3. If intersection exists:
        - Save intersection as a new STEP file.
        - Visualize geometry and plane in a PNG image.
    4. Logs OCC internal output to 'lib_occ.log' in the input file's folder.

    Raises:
        argparse.ArgumentTypeError: If --in-plane does not contain exactly 6 floats.
        RuntimeError: If reading/writing STEP files fails, or intersection fails.
    """

    parser = argparse.ArgumentParser(description="Script for identify the intersection between a given geometry and a given plane")
    
    parser.add_argument("--in-step", required=True, help="Filepath of .stp file with the geometry under investigation",
        type=common_lib.check_file)
    
    parser.add_argument("--in-plane", required=True, nargs='+', type=float,
        help="Plane in a point-normal definition, 6 floats are required the first 3 are the point coordinates x, y, z and the rest 3 are the normal directions nx, ny, nz")
    
    parser.add_argument("--out-step", required=False,
        help="Filepath of .stp file with the intersection, if not given the output file will be saved at the parent directory of initial .stp file with the name intersection.stp", default= "intersection.stp")
    
    args = parser.parse_args()

    step_file       = args.in_step
    output_filename = args.out_step

    if len(args.in_plane) != 6:
        raise argparse.ArgumentTypeError("Exactly 6 numbers should be provided with argument --in-plane, the first 3 should be the point coordinates x, y, z and the rest 3 should be the normal directions nx, ny, nz")

    plane_point     = args.in_plane[:3]       
    plane_normal    = args.in_plane[3:]
    
    output_log                         = common_lib.output_file_path(step_file, "lib_occ.log")
    shape, plane, result_shape, result = step_file_lib.find_intersection(step_file, plane_point, plane_normal)

    if result:
        # Combine geometry with plane for visualization purposes
        with common_lib.redirect_output(output_log):
            dx, dy, dz  = step_file_lib.compute_dimensions(shape)
            dimension   = max(dx, dy, dz)
            display     = step_file_lib.combine_geometry_plane(shape, plane, dimension)

            # Print geometry
            root, name = os.path.split(step_file)
            name, ext  = os.path.splitext(name)
            output_png = common_lib.output_file_path(step_file, name+".png")
            step_file_lib.plot_geometry(display, output_png)
            
        # Write the result to a new STEP file
        output_file = common_lib.output_file_path(step_file, output_filename)
        status      = step_file_lib.write_step_geometry(result_shape, output_file)

        if status != True:
            raise RuntimeError("Intersection found but failed to write STEP file: {}".format(output_file))
        else:
            print("Intersection found and written to: {}".format(output_filename))
            print("A png file with the geometry and the plane has been written to: {}".format(output_png))

    else:
        print("No intersection found")

    return

##########################################
    
if __name__ == "__main__":
    
    main()
    
##########################################
