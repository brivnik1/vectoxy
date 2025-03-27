import streamlit as st
import numpy as np
from bs4 import BeautifulSoup
import re
from svgpathtools import parse_path

def extract_coordinates_from_svg(svg_file, flatten_tolerance=5):
    with open(svg_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    soup = BeautifulSoup(content, "xml")
    x_coords, y_coords = [], []
    
    for path in soup.find_all("path"):
        d = path.get("d", "")
        parsed_path = parse_path(d)
        
        for segment in parsed_path:
            points = segment.point(np.linspace(0, 1, flatten_tolerance))
            for point in points:
                x_coords.append(point.real)
                y_coords.append(point.imag)
    
    return np.array(x_coords), np.array(y_coords)

def normalize_coordinates(x_coords, y_coords):
    """Normalize coordinates to range -1 to 1."""
    min_x, max_x = np.min(x_coords), np.max(x_coords)
    min_y, max_y = np.min(y_coords), np.max(y_coords)
    
    x_coords = 2 * (x_coords - min_x) / (max_x - min_x) - 1
    y_coords = 2 * (y_coords - min_y) / (max_y - min_y) - 1
    
    return x_coords, y_coords

def save_to_file(filename, data):
    with open(filename, "w") as f:
        f.write("\n".join(map(str, data)))

def main():
    st.title("Vector to Coordinate Converter (Pure Python)")
    
    uploaded_file = st.file_uploader("Upload an SVG file", type=["svg"])
    flatten_tolerance = st.slider("Bezier Flattening Strength", 1, 20, 5)
    
    if uploaded_file is not None:
        temp_svg_path = f"/tmp/{uploaded_file.name}"
        with open(temp_svg_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        x_coords, y_coords = extract_coordinates_from_svg(temp_svg_path, flatten_tolerance)
        x_coords, y_coords = normalize_coordinates(x_coords, y_coords)
        
        output_x = f"/tmp/optimized_x.txt"
        output_y = f"/tmp/optimized_y.txt"
        
        save_to_file(output_x, x_coords)
        save_to_file(output_y, y_coords)
        
        st.success("Processing complete! Download your coordinate files below.")
        st.download_button("Download X Coordinates", open(output_x, "r").read(), "optimized_x.txt")
        st.download_button("Download Y Coordinates", open(output_y, "r").read(), "optimized_y.txt")

if __name__ == "__main__":
    main()

