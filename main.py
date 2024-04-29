import streamlit as st
import SimpleITK as sitk
import numpy as np
import tempfile
import os
import nibabel as nib
import plotly.graph_objects as go

def load_and_store_dicom_series(directory, session_key):
    if session_key not in st.session_state:
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(directory)
        reader.SetFileNames(dicom_names)
        image_sitk = reader.Execute()
        image_np = sitk.GetArrayFromImage(image_sitk)
        st.session_state[session_key] = image_np
    return st.session_state[session_key]

def load_nifti_file(filepath, session_key):
    if session_key not in st.session_state:
        nifti_img = nib.load(filepath)
        image_np = np.asanyarray(nifti_img.dataobj)
        st.session_state[session_key] = image_np
    return st.session_state[session_key]

def plot_slice(slice_data, orientation):
    if orientation == 'axial':
        return go.Figure(data=go.Heatmap(z=slice_data, colorscale='gray', zmin=np.min(slice_data), zmax=np.max(slice_data)))
    elif orientation == 'coronal':
        return go.Figure(data=go.Heatmap(z=slice_data.T, colorscale='gray', zmin=np.min(slice_data), zmax=np.max(slice_data)))
    elif orientation == 'sagittal':
        return go.Figure(data=go.Heatmap(z=slice_data.T, colorscale='gray', zmin=np.min(slice_data), zmax=np.max(slice_data)))

def main():
    st.set_page_config(page_title='DICOM Viewer', layout="wide", page_icon="")

    st.title("DICOM Series Viewer")

    # Provide instructions for file upload
    st.markdown("Upload DICOM or NIfTI files below:")

    uploaded_files = st.file_uploader("Choose DICOM or NIfTI Files", accept_multiple_files=True, type=["dcm", "nii", "nii.gz"], key="file_uploader")
    
    if uploaded_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            is_nifti = False
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.read()
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(bytes_data)
                if uploaded_file.name.endswith(('.nii', '.nii.gz')):
                    is_nifti = True
            
            if is_nifti:
                image_np = load_nifti_file(file_path, "nifti_image_data")
            else:
                image_np = load_and_store_dicom_series(temp_dir, "dicom_image_data")


        col1, col2, col3 = st.columns(3)

        # Display labels for each view with unique colors
        col1.markdown("<div class='view-label-axial'>Axial</div>", unsafe_allow_html=True)
        col2.markdown("<div class='view-label-coronal'>Coronal </div>", unsafe_allow_html=True)
        col3.markdown("<div class='view-label-sagittal'>Sagittal </div>", unsafe_allow_html=True)
        if is_nifti:
            with col1:
                axial_slice_num = st.slider('Axial Slice', 0, image_np.shape[2] - 1, 0, key="axial_slider")
                fig = plot_slice(image_np[:, :, axial_slice_num], 'axial')
                st.plotly_chart(fig)

            with col2:
                coronal_slice_num = st.slider('Coronal Slice', 0, image_np.shape[1] - 1, 0, key="coronal_slider")
                fig = plot_slice(image_np[:, coronal_slice_num, :], 'coronal')
                st.plotly_chart(fig)

            with col3:
                sagittal_slice_num = st.slider('Sagittal Slice', 0, image_np.shape[0] - 1, 0, key="sagittal_slider")
                fig = plot_slice(image_np[sagittal_slice_num, :, :], 'sagittal')
                st.plotly_chart(fig)

        else:
            with col1:
                axial_slice_num = st.slider('Axial Slice', 0, image_np.shape[0] - 1, 0, key="axial_slider")
                fig = plot_slice(image_np[axial_slice_num, :, :], 'axial')
                st.plotly_chart(fig)

            with col2:
                coronal_slice_num = st.slider('Coronal Slice', 0, image_np.shape[1] - 1, 0, key="coronal_slider")
                fig = plot_slice(image_np[:, coronal_slice_num, :], 'coronal')
                st.plotly_chart(fig)

            with col3:
                sagittal_slice_num = st.slider('Sagittal Slice', 0, image_np.shape[2] - 1, 0, key="sagittal_slider")
                fig = plot_slice(image_np[:, :, sagittal_slice_num], 'sagittal')
                st.plotly_chart(fig)

if __name__ == "__main__":
    main()