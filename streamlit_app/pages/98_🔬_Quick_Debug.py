"""
Quick Debug - Minimum diagnostic info
"""
import streamlit as st
from pathlib import Path
import os

st.set_page_config(page_title="Quick Debug", page_icon="🔬", layout="wide")

st.title("🔬 Quick Debug")

# 1. CWD
st.subheader("1. Current Working Directory")
cwd = Path.cwd()
st.code(str(cwd))

# 2. Check data directories
st.subheader("2. Data Directories Check")

checks = [
    ("cwd/data", Path.cwd() / "data"),
    ("cwd/shared/data", Path.cwd() / "shared" / "data"),
]

for name, path in checks:
    exists = path.exists()
    if exists:
        json_files = list(path.glob("*.json"))
        st.success(f"✅ {name}: {len(json_files)} JSON files")

        # Check specific files
        diseases = path / "diseases.json"
        pests = path / "pests.json"
        weeds = path / "weeds.json"

        st.write(f"  - diseases.json: {'✅' if diseases.exists() else '❌'}")
        st.write(f"  - pests.json: {'✅' if pests.exists() else '❌'}")
        st.write(f"  - weeds.json: {'✅' if weeds.exists() else '❌'}")

        if json_files:
            with st.expander(f"All files in {name}"):
                for f in sorted(json_files):
                    st.text(f"{f.name} ({f.stat().st_size} bytes)")
    else:
        st.error(f"❌ {name}: NOT FOUND")
        st.text(f"   Path: {path}")

# 3. Test loading
st.subheader("3. Test Reference Loader")

try:
    from utils.reference_loader import load_diseases, load_pests, load_weeds

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.spinner("Loading diseases..."):
            diseases = load_diseases()
            if diseases:
                st.success(f"✅ Diseases: {len(diseases)} categories")
            else:
                st.error("❌ Diseases: FAILED")

    with col2:
        with st.spinner("Loading pests..."):
            pests = load_pests()
            if pests:
                st.success(f"✅ Pests: {len(pests)} categories")
            else:
                st.error("❌ Pests: FAILED")

    with col3:
        with st.spinner("Loading weeds..."):
            weeds = load_weeds()
            if weeds:
                st.success(f"✅ Weeds: {len(weeds)} categories")
            else:
                st.error("❌ Weeds: FAILED")

except ImportError as e:
    st.error(f"Import error: {e}")
except Exception as e:
    st.error(f"Error: {e}")

# 4. Environment
st.subheader("4. Environment")
st.text(f"Streamlit Cloud: {os.environ.get('STREAMLIT_SHARING_MODE', 'false')}")
st.text(f"Python: {os.sys.version.split()[0]}")

# 5. Module location
st.subheader("5. Utils Module Location")
try:
    import utils.reference_loader as rl
    st.code(rl.__file__)
except Exception as e:
    st.error(str(e))
