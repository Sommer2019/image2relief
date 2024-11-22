import numpy as np
from PIL import Image
from stl import mesh

# Load the image and convert to grayscale
def load_image(image_path):
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    return np.array(img)

# Convert image to height map and create vertices
def image_to_height_map(image_array, scale=1.0, height_scale=10.0):
    height, width = image_array.shape
    x = np.linspace(0, width, width) * scale
    y = np.linspace(0, height, height) * scale
    xv, yv = np.meshgrid(x, y)

    # Normalize pixel values (0 to 255) and scale height
    z = (image_array / 255.0) * height_scale
    return xv, yv, z

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
def image_to_stl(image_path, output_filename='output.stl', scale=1.0, height_scale=10.0):
    image_array = load_image(image_path)
    xv, yv, z = image_to_height_map(image_array, scale, height_scale)
    vertices, faces = create_faces(xv, yv, z)
    generate_stl(vertices, faces, output_filename)

# Example usage
image_to_stl('image.jpg', 'output.stl', scale=0.1, height_scale=5.0)
