import streamlit as st
import numpy as np
from PIL import Image
import os
from pathlib import Path
import io
import matplotlib.pyplot as plt

st.title("Synthetic NDVI Converter for Drought Estimation")
st.write("""
This app converts RGB satellite images to synthetic NDVI images.
You can either upload a single image or process an entire directory of images. Think of google maps images, but now you can turn them into synthetic NDVI images for drought estimation
""")


def calculate_synthetic_ndvi(image_array):
    image_float = image_array.astype(float)
    r = image_float[:, :, 0]
    g = image_float[:, :, 1]
    b = image_float[:, :, 2]
    nir_approx = (r + g + b) / 3
    epsilon = 1e-8
    ndvi = (nir_approx - r) / (nir_approx + r + epsilon)
    ndvi = (ndvi + 1) / 2
    return ndvi


def process_single_image(image):
    image_array = np.array(image)
    ndvi = calculate_synthetic_ndvi(image_array)
    return ndvi


uploaded_file = st.file_uploader("Select an RGB satellite image of a landscape of your choosing",
                                 type=['png', 'jpg', 'jpeg', 'tif', 'tiff'])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    ndvi = process_single_image(image)

    # Display NDVI image using a colormap
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.imshow(ndvi, cmap='RdYlGn')
    ax.set_title("NDVI Image")
    ax.axis('off')
    st.pyplot(fig)

    # Download button for the single image processing
    buf = io.BytesIO()
    plt.savefig(buf, format='PNG')
    st.download_button(
        label="Download NDVI Image",
        data=buf.getvalue(),
        file_name="ndvi_result.png",
        mime="image/png"
    )

directory = st.text_input("Enter directory path (.jpg, .jpeg, .png, .tiff, .tif")


def process_directory(directory_path):
    processed_images = []
    valid_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
    for file_path in Path(directory_path).glob('*'):
        if file_path.suffix.lower() in valid_extensions:
            try:
                image = Image.open(file_path)
                ndvi = process_single_image(image)
                processed_images.append((file_path.name, ndvi))
            except Exception as e:
                st.error(f"Error processing {file_path.name}: {str(e)}")
    return processed_images


if directory and st.button("Process Directory"):
    if os.path.isdir(directory):
        processed_images = process_directory(directory)
        if processed_images:
            st.success(f"Processed {len(processed_images)} images")
            output_dir = os.path.join(directory, "ndvi_results")
            os.makedirs(output_dir, exist_ok=True)
            for filename, ndvi in processed_images:
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(ndvi, cmap='RdYlGn')
                ax.set_title(f"NDVI for {filename}")
                ax.axis('off')
                output_path = os.path.join(output_dir, f"ndvi_{filename.split('.')[0]}.png")
                plt.savefig(output_path)
            st.success(f"Results saved to {output_dir}")
        else:
            st.warning("No valid images found")
    else:
        st.error("Invalid directory path")