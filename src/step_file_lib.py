"""

This library provides utilities for working with STEP geometry using pythonocc-core.

Main features:
- Read and write STEP files
- Compute bounding box dimensions of a geometry
- Create planes in point-normal form
- Compute intersections between planes and geometry
- Visualize shapes and save screenshots

Dependencies:
- pythonocc-core
- common_lib (local utility module for logging and output redirection)
"""

##########################################

from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Pln
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib

import os
import common_lib

##########################################

global log_file 
log_file = "lib_occ.log"

##########################################

def read_step_geometry(step_filename):
    """
    Reads a STEP file and returns the TopoDS_Shape geometry.

    Parameters:
        step_filename (str): Path to the STEP file.

    Returns:
        TopoDS_Shape: Loaded geometry shape.

    Raises:
        RuntimeError: If the STEP file cannot be read or contains no geometry.
    """

    output_log = common_lib.output_file_path(step_filename, log_file)

    with common_lib.redirect_output(output_log):
        step_reader = STEPControl_Reader()
        status = step_reader.ReadFile(step_filename)
    if status != 1:
        raise RuntimeError("Failed to read STEP file: {}".format(step_filename))
    else:
        print("STEP file has been read sucessfully")

    with common_lib.redirect_output(output_log):
        ok = step_reader.TransferRoots()
    if not ok:
        raise RuntimeError("Failed to transfer STEP file contents.")
    else:
        print("STEP file contents have been transfered sucessfully")

    with common_lib.redirect_output(output_log):
        shape = step_reader.OneShape()
    if shape.IsNull():
        raise RuntimeError("STEP file contains no geometry.")

    return shape

##########################################

def write_step_geometry(shape, output_file):
    """
    Writes a TopoDS_Shape to a STEP file.

    Parameters:
        shape (TopoDS_Shape): The shape to export.
        output_file (str): Destination STEP file path.

    Returns:
        int: Status code returned by STEPControl_Writer.Write (1 means success).
    """

    output_log = common_lib.output_file_path(output_file, log_file)

    with common_lib.redirect_output(output_log):
        step_writer = STEPControl_Writer()
        step_writer.Transfer(shape, STEPControl_AsIs)
        status = step_writer.Write(output_file)

    return status

##########################################

def compute_dimensions(shape):
    """
    Computes the dimensions (dx, dy, dz) of the bounding box of a shape.

    Parameters:
        shape (TopoDS_Shape): Geometry shape.

    Returns:
        tuple: Dimensions (dx, dy, dz).
    """

    # Compute bounding box
    bbox = Bnd_Box()
    brepbndlib.Add(shape, bbox)

    # Get min and max coordinates
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()

    # Dimensions
    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin

    return dx, dy, dz

##########################################

def create_plane_point_normal(plane_point, plane_normal):
    """
    Creates a gp_Pln plane using a point and normal vector.

    Parameters:
        plane_point (list or tuple): [x, y, z] coordinates of a point on the plane.
        plane_normal (list or tuple): [nx, ny, nz] normal vector.

    Returns:
        gp_Pln: Constructed plane.
    """

    point  = gp_Pnt(*plane_point)
    normal = gp_Dir(*plane_normal)
    plane  = gp_Pln(point, normal)

    return plane

##########################################

def find_intersection(step_filename, plane_point, plane_normal):
    """
    Computes the intersection between a STEP geometry and a plane.

    Parameters:
        step_filename (str): Path to the STEP file.
        plane_point (list or tuple): [x, y, z] coordinates of a point on the plane.
        plane_normal (list or tuple): [nx, ny, nz] normal vector.

    Returns:
        tuple: (shape, plane, result_shape, result)
            - shape (TopoDS_Shape): Loaded geometry from STEP file.
            - plane (gp_Pln): Created plane.
            - result_shape (TopoDS_Shape): Intersection geometry shape.
            - result (bool): True if intersection contains edges; False otherwise.

    Raises:
        RuntimeError: If the STEP file cannot be read or intersection computation fails.
    """
    
    result = False

    # Load STEP file
    shape = read_step_geometry(step_filename)
    
    # Create plane from point-normal
    plane = create_plane_point_normal(plane_point, plane_normal)
    
    # Compute intersection using BRepAlgoAPI_Section
    output_log = common_lib.output_file_path(step_filename, log_file)

    with common_lib.redirect_output(output_log):
        section = BRepAlgoAPI_Section(shape, plane, True)
        section.ComputePCurveOn1(True)
        section.Approximation(True)
        section.Build()

    if not section.IsDone():
        raise RuntimeError("Failed to compute intersection between plane and geometry.")
    else:
        print("Computation of intersection finished sucessfully")

    # Check if intersection result is not empty
    with common_lib.redirect_output(output_log):
        result_shape = section.Shape()
        explorer = TopExp_Explorer(result_shape, TopAbs_EDGE)
        has_edges = explorer.More() 

    if has_edges:
        result = True
    
    return shape, plane, result_shape, result

##########################################

def plot_geometry(display, output):
    """
    Renders the display scene and saves a screenshot to a PNG file.

    Parameters:
        display: Display object returned by init_display().
        output (str): Path to save the PNG image.

    Returns:
        None
    """

    display.FitAll()
    display.Repaint()

    display.ExportToImage(output)

    return

##########################################

def create_face(plane, dimension):
    """
    Creates a finite rectangular face on the given plane for visualization.

    Parameters:
        plane (gp_Pln): The plane to create the face on.
        dimension (float): Half-size of the face in both u and v directions.

    Returns:
        TopoDS_Face: The created face.
    """

    face = BRepBuilderAPI_MakeFace(plane, -dimension, dimension, -dimension, dimension).Face()

    return face

##########################################

def combine_geometry_plane(shape, plane, dimension):
    """
    Displays the STEP shape together with a finite face representing the plane.

    Parameters:
        shape (TopoDS_Shape): Geometry shape.
        plane (gp_Pln): Plane.
        dimension (float): Half-size of the plane face.

    Returns:
        display: Display object from init_display() for further use.
    """

    # Make a finite face on the plane for visualization purposes
    face = create_face(plane, dimension)

    # Initialize the viewer
    display, start_display, _, _ = init_display()

    # Display both: STEP shape and plane face
    display.DisplayShape(shape, update=True)
    display.DisplayShape(face, update=True, color='LIGHTBLUE', transparency=0.2)

    return display

##########################################




