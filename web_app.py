import streamlit as st
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
import hashlib

st.set_page_config(page_title="PDF Digital Signature Tool", layout="wide")

st.title("🔐 PDF Digital Signature Tool (DSA)")

# Session State Initialization
if "private_key" not in st.session_state:
    st.session_state.private_key = None
if "public_key" not in st.session_state:
    st.session_state.public_key = None
if "signature" not in st.session_state:
    st.session_state.signature = None

# Sidebar
st.sidebar.header("Key Management")

if st.sidebar.button("Generate Keys"):
    private_key = dsa.generate_private_key(key_size=2048)
    public_key = private_key.public_key()

    st.session_state.private_key = private_key
    st.session_state.public_key = public_key

    st.sidebar.success("Keys Generated Successfully")

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])

if uploaded_file:
    pdf_data = uploaded_file.read()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 SHA-256 Hash")
        hash_value = hashlib.sha256(pdf_data).hexdigest()
        st.code(hash_value)

    with col2:
        st.subheader("🖊 Digital Signature")

        if st.button("Sign PDF"):
            if st.session_state.private_key:
                signature = st.session_state.private_key.sign(
                    pdf_data,
                    hashes.SHA256()
                )
                st.session_state.signature = signature
                st.success("PDF Signed Successfully")

                st.download_button(
                    label="Download Signature File",
                    data=signature,
                    file_name="signature.sig"
                )
            else:
                st.error("Generate keys first")

    # Signature Upload for Verification
    st.subheader("🔍 Verify Signature")

    uploaded_signature = st.file_uploader("Upload Signature File (.sig)", type=["sig"])

    if st.button("Verify Signature"):
        if st.session_state.public_key and uploaded_signature:
            try:
                signature_data = uploaded_signature.read()

                st.session_state.public_key.verify(
                    signature_data,
                    pdf_data,
                    hashes.SHA256()
                )

                st.success("✅ Signature VALID — Document Authentic")

            except InvalidSignature:
                st.error("❌ Signature INVALID — Document Modified")
        else:
            st.error("Missing public key or signature file")