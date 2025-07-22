import streamlit as st
import pandas as pd
from io import StringIO
from sample_data import load_garden_data, get_gardens, get_sample_size, get_tree_count

st.set_page_config(page_title="Garden Sampling App", layout="wide")
st.title("🌱 Tree Sampling Application")

# Initialize session state
for key in ['step', 'tree_data', 'selected_gardens']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.step is None:
    st.session_state.step = 1

# Load random garden dataset
garden_data = load_garden_data()

# Step 1: Select Area
if st.session_state.step == 1:
    st.header("Step 1: Select Area")
    area = st.selectbox("Choose an Area", ["North", "South"])
    if st.button("Next"):
        st.session_state.area = area
        st.session_state.step = 2

# Step 2: Select Age Bucket
elif st.session_state.step == 2:
    st.header("Step 2: Select Age Bucket")
    age_bucket = st.selectbox("Choose Age Bucket", ["0-5", "6-10", "11-15"])
    if st.button("Next"):
        st.session_state.age_bucket = age_bucket
        st.session_state.sample_size = get_sample_size(st.session_state.area, age_bucket)
        st.session_state.step = 3

# Step 3: Sample Gardens
elif st.session_state.step == 3:
    st.header("Step 3: Garden Sampling")
    filtered = get_gardens(st.session_state.area, st.session_state.age_bucket, garden_data)
    st.write(f"🎯 Total Matching Gardens: {len(filtered)}")
    st.write(f"📌 Ideal Sample Size: {st.session_state.sample_size}")

    if st.checkbox("Auto-select random gardens"):
        selected = filtered.sample(n=st.session_state.sample_size)
    else:
        selected_ids = st.multiselect("Manually Select Gardens", filtered["garden_id"].tolist())
        selected = filtered[filtered["garden_id"].isin(selected_ids)]

    st.dataframe(selected)

    if st.button("Confirm Sample"):
        st.session_state.selected_gardens = selected
        st.session_state.tree_plan = {
            row["garden_id"]: get_tree_count(row["garden_area_ha"])
            for _, row in selected.iterrows()
        }
        st.session_state.step = 4

# Step 4: Input Tree Data
elif st.session_state.step == 4:
    st.header("Step 4: Enter Tree Observations")

    if st.session_state.tree_data is None:
        st.session_state.tree_data = []

    for _, row in st.session_state.selected_gardens.iterrows():
        garden_id = row["garden_id"]
        garden_area = row["garden_area_ha"]
        tree_count = st.session_state.tree_plan[garden_id]

        st.markdown(f"### 🌿 Garden {garden_id} | Area: {garden_area} ha | Trees: {tree_count}")
        for i in range(1, tree_count + 1):
            col1, col2 = st.columns(2)
            with col1:
                height = st.text_input(f"Garden {garden_id} - Tree {i} - Height (m)", key=f"{garden_id}_{i}_height")
            with col2:
                yield_ = st.text_input(f"Garden {garden_id} - Tree {i} - Yield (kg)", key=f"{garden_id}_{i}_yield")

            st.session_state.tree_data.append({
                "Region": st.session_state.area,
                "Age Category": st.session_state.age_bucket,
                "Garden ID": garden_id,
                "Garden Area (ha)": garden_area,
                "Tree Number": i,
                "Height (m)": height,
                "Yield (kg)": yield_
            })

    if st.button("✅ Save & Generate Report"):
        st.session_state.step = 5

# Step 5: Generate Downloadable Report
elif st.session_state.step == 5:
    st.success("🎉 Data Saved Successfully!")

    df = pd.DataFrame(st.session_state.tree_data)

    # Add summary at the top of CSV
    summary = pd.DataFrame([{
        "Region": st.session_state.area,
        "Age Category": st.session_state.age_bucket,
        "Gardens Sampled": len(st.session_state.selected_gardens),
        "Total Trees Sampled": len(df)
    }])

    output = pd.concat([summary, df], ignore_index=True)

    st.subheader("📦 Final Output")
    st.dataframe(df)

    csv_buffer = StringIO()
    output.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button("📥 Download CSV Report",
                       data=csv_data,
                       file_name="tree_sampling_report.csv",
                       mime="text/csv")
