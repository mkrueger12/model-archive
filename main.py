import streamlit as st
import os
from huggingface_hub import hf_hub_download, list_repo_files
from google.cloud import storage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

st._gather_metrics = False

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "cancel_upload" not in st.session_state:
    st.session_state.cancel_upload = False


def check_password(password):
    """Verify the entered password."""
    return password == os.environ.get("APP_PASSWORD")


def login():
    """Handle the login process."""
    st.session_state.logged_in = check_password(st.session_state.password)


def cancel_upload():
    """Set the cancel flag to True."""
    logging.warning("Transfer cancelled")
    st.session_state.cancel_upload = True


def download_and_upload_to_gcs(repo_id, bucket_name, gcs_prefix=None):
    try:
        # Reset cancel flag at the start of transfer
        st.session_state.cancel_upload = False

        # Initialize Google Cloud Storage client
        logging.info("Initializing Google Cloud Storage client...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        # List all files in the repository
        files = list_repo_files(repo_id)
        logging.info(f"Found {len(files)} files in the repository.")

        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text(f"Found {len(files)} files in the repository.")

        for idx, file in enumerate(files):
            # Check if cancel was requested
            if st.session_state.cancel_upload:
                status_text.text("Transfer cancelled by user!")
                return False

            try:
                status_text.text(f"Processing: {file}")

                # Download file
                local_path = hf_hub_download(
                    repo_id=repo_id, filename=file, local_files_only=False
                )

                # Create GCS blob path
                blob_path = os.path.join(gcs_prefix, file) if gcs_prefix else file
                blob = bucket.blob(blob_path)

                # Upload to GCS
                blob.upload_from_filename(local_path)
                logging.info(f"Uploaded {blob_path} to GCS.")

                # Clean up
                os.remove(local_path)

                # Update progress
                progress_bar.progress((idx + 1) / len(files))

            except Exception as e:
                st.error(f"Error processing {file}: {str(e)}")
                logging.error(f"Error processing {file}: {str(e)}")

        status_text.text("Processing complete!")
        return True

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def main():
    st.title("HuggingFace to Google Cloud Storage Transfer")

    # Login section
    if not st.session_state.logged_in:
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=login)
        return

    # Main app section (only shown when logged in)
    repo_id = st.text_input("Repository ID", placeholder="e.g., facebook/bart-large")

    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("Start Transfer")
    with col2:
        st.button("Cancel Transfer", on_click=cancel_upload)

    if start_button:
        if not repo_id:
            st.error("Repository ID is required!")
            return

        download_and_upload_to_gcs(
            repo_id=repo_id,
            bucket_name=os.environ.get("BUCKET_NAME"),
            gcs_prefix=repo_id,
        )


if __name__ == "__main__":
    main()
