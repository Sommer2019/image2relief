import numpy as np
from PIL import Image, ImageOps
from stl import mesh
from scipy.ndimage import gaussian_filter

# Load the image and convert to grayscale
def load_image(image_path):
    imgimp = Image.open(image_path).convert('L')  # Convert to grayscale
    img = ImageOps.mirror(imgimp) # Mirror the image, so the output is correct
    return np.array(img)

# Convert image to height map and create vertices
def image_to_height_map(image_array, scale=1.0, height_scale=10.0, smooth_factor=1.0):
    height, width = image_array.shape
    x = np.linspace(0, width, width) * scale
    y = np.linspace(0, height, height) * scale
    xv, yv = np.meshgrid(x, y)

    # Normalize pixel values (0 to 255) and scale height
    z = (image_array / 255.0) * height_scale

    # Apply Gaussian smoothing to the height map
    z_smooth = gaussian_filter(z, sigma=smooth_factor)

    return xv, yv, z_smooth

# Create faces for the 3D relief mesh
def create_faces(xv, yv, z):
    height, width = z.shape
    vertices = np.zeros((height * width, 3))

    # Create vertices
    for i in range(height):
        for j in range(width):
            vertices[i * width + j] = [xv[i, j], yv[i, j], z[i, j]]

    faces = []
    for i in range(height - 1):
        for j in range(width - 1):
            # Create two triangles per quad
            v1 = i * width + j
            v2 = v1 + 1
            v3 = v1 + width
            v4 = v3 + 1

            # Triangle 1
            faces.append([v1, v2, v3])
            # Triangle 2
            faces.append([v2, v4, v3])

    return vertices, np.array(faces)

# Create STL mesh
def generate_stl(vertices, faces, output_filename='output.stl'):
    relief_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, face in enumerate(faces):
        for j in range(3):
            relief_mesh.vectors[i][j] = vertices[face[j], :]

    relief_mesh.save(output_filename)
    print(f"STL file saved as {output_filename}")

# Main function
def image_to_stl(image_path, output_filename='output.stl', scale=1.0, height_scale=10.0, smooth_factor=1.0):
    image_array = load_image(image_path)
    xv, yv, z = image_to_height_map(image_array, scale, height_scale, smooth_factor)
    vertices, faces = create_faces(xv, yv, z)
    generate_stl(vertices, faces, output_filename)

if __name__ == "__main__":
    # Get user input
    image_path = input("Enter the image filename (e.g., image.png): ")
    output_filename = input("Enter the output STL filename (e.g., output.stl): ")
    scale = float(input("Enter the scale (e.g., 0.1 for 10% scale): "))
    height_scale = float(input("Enter the height scale (e.g., 5.0): "))
    smooth_factor = float(input("Enter the smooth factor for edges (e.g., 1.0): "))

    # Generate the STL
    image_to_stl(image_path, output_filename, scale, height_scale, smooth_factor)
