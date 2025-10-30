"""
Debug page to check file paths in Streamlit Cloud
"""
import streamlit as st
from pathlib import Path
import os
import sys

st.set_page_config(page_title="Debug Paths", page_icon="🔧", layout="wide")

st.title("🔧 Debug: File Paths")

st.markdown("---")

# Current working directory
st.subheader("📂 Current Working Directory")
cwd = Path.cwd()
st.code(str(cwd))

# __file__ path
st.subheader("📄 __file__ Path")
file_path = Path(__file__)
st.code(str(file_path))

# Parent directories
st.subheader("📁 Parent Directories")
st.code(f"""
__file__:              {file_path}
parent (pages):        {file_path.parent}
parent.parent (app):   {file_path.parent.parent}
parent.parent.parent:  {file_path.parent.parent.parent}
""")

# Candidate paths for references
st.subheader("🔍 Candidate Paths for 'fertilizers.json'")

candidate_paths = [
    Path(__file__).parent.parent / "data" / "fertilizers.json",
    Path(__file__).parent.parent / "streamlit_app" / "data" / "fertilizers.json",
    Path(__file__).parent.parent / "shared" / "data" / "fertilizers.json",
    Path.cwd() / "data" / "fertilizers.json",
    Path.cwd() / "streamlit_app" / "data" / "fertilizers.json",
    Path.cwd() / "streamlit_app" / "shared" / "data" / "fertilizers.json",
    Path(__file__).resolve().parent.parent.parent / "data" / "fertilizers.json",
    Path(__file__).resolve().parent.parent.parent / "shared" / "data" / "fertilizers.json",
]

st.markdown("#### Checking paths:")

for i, p in enumerate(candidate_paths, 1):
    exists = p.exists()
    status = "✅ EXISTS" if exists else "❌ NOT FOUND"

    with st.expander(f"{status} - Path #{i}"):
        st.code(str(p.resolve()))

        if exists:
            st.success(f"File exists! Size: {p.stat().st_size} bytes")
            # Try to read first few lines
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    preview = f.read(200)
                    st.text(f"Preview:\n{preview}...")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        else:
            # Check if parent directory exists
            parent_exists = p.parent.exists()
            st.warning(f"Parent directory exists: {parent_exists}")
            if parent_exists:
                st.info(f"Parent path: {p.parent}")
                # List files in parent directory
                try:
                    files = list(p.parent.glob("*.json"))
                    if files:
                        st.write("JSON files in parent directory:")
                        for f in files[:10]:  # Show first 10
                            st.text(f"  - {f.name}")
                except Exception as e:
                    st.error(f"Error listing files: {e}")

# System info
st.markdown("---")
st.subheader("💻 System Info")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Python sys.path:**")
    for path in sys.path[:5]:
        st.text(path)

with col2:
    st.markdown("**Environment:**")
    st.text(f"Python: {sys.version.split()[0]}")
    st.text(f"Platform: {sys.platform}")

    # Check if running on Streamlit Cloud
    is_cloud = os.environ.get('STREAMLIT_SHARING_MODE') == 'true'
    st.text(f"Streamlit Cloud: {is_cloud}")

# List all files in data directories
st.markdown("---")
st.subheader("📋 All files in data/ directories")

data_dirs = [
    Path.cwd() / "data",
    Path.cwd() / "streamlit_app" / "data",
    Path.cwd() / "streamlit_app" / "shared" / "data",
    Path(__file__).parent.parent / "data",
    Path(__file__).parent.parent / "shared" / "data",
]

for data_dir in data_dirs:
    with st.expander(f"📁 {data_dir}"):
        if data_dir.exists():
            try:
                files = list(data_dir.glob("*.*"))
                st.success(f"Directory exists! {len(files)} files found")
                for f in sorted(files):
                    st.text(f"  - {f.name} ({f.stat().st_size} bytes)")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Directory does not exist")

# Try importing and using the reference loader
st.markdown("---")
st.subheader("🧪 Test Reference Loader")

try:
    from utils.reference_loader import load_reference

    st.info("✅ reference_loader module imported successfully")

    if st.button("Test load_reference('fertilizers.json')"):
        with st.spinner("Loading..."):
            data = load_reference("fertilizers.json", show_error=True)

            if data:
                st.success(f"✅ Loaded successfully! {len(data)} categories found")
                st.json(list(data.keys())[:5])  # Show first 5 keys
            else:
                st.error("❌ Failed to load")

except ImportError as e:
    st.error(f"❌ Failed to import reference_loader: {e}")
except Exception as e:
    st.error(f"❌ Error: {e}")

# Footer
st.markdown("---")
st.caption("Use this page to debug file path issues in Streamlit Cloud")
