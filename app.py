import streamlit as st
from supabase import create_client
from datetime import datetime

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Dr. Tag Eye Clinic Management System",
    page_icon="👁️",
    layout="wide"
)

# ---------------- SUPABASE CONNECTION ----------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SESSION STATE ----------------

if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None

# ---------------- TITLE ----------------

st.title("👁️ Dr. Tag Eye Clinic Management System")

# ---------------- SIDEBAR ----------------

menu = st.sidebar.selectbox("Menu", ["Add Patient", "View Patients"])

# =====================================================
# ---------------- ADD PATIENT ----------------
# =====================================================

if menu == "Add Patient":

    st.subheader("Add New Patient")

    name = st.text_input("Full Name")
    age = st.text_input("Age")
    gender = st.selectbox("Gender", ["Male", "Female"])
    phone = st.text_input("Phone")

    if st.button("Save Patient"):

        if not name.strip():
            st.warning("Patient name is required!")

        else:
            try:
                res = (
                    supabase
                    .schema("public")
                    .table("patients")
                    .insert({
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "phone": phone
                    })
                    .execute()
                )

                if res.data:
                    st.success("Patient Added Successfully!")
                else:
                    st.error("Insert failed (check RLS or table name).")

            except Exception as e:
                st.error(f"Error: {e}")

# =====================================================
# ---------------- VIEW PATIENTS ----------------
# =====================================================

if menu == "View Patients":

    if st.session_state.selected_patient is None:

        st.subheader("Patients List")

        col1, col2 = st.columns(2)

        with col1:
            search_name = st.text_input("🔍 Search by Name")

        with col2:
            search_phone = st.text_input("🔍 Search by Phone")

        try:
            query = (
                supabase
                .schema("public")
                .table("patients")
                .select("*")
            )

            if search_name:
                query = query.ilike("name", f"%{search_name}%")

            if search_phone:
                query = query.ilike("phone", f"%{search_phone}%")

            patients = query.execute().data

        except Exception as e:
            st.error(f"Fetch error: {e}")
            patients = []

        if not patients:
            st.info("No patients found.")
        else:
            for patient in patients:

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"### {patient['name']}")
                    st.write(f"📞 {patient['phone']}")

                with col2:
                    if st.button("Open", key=f"open_{patient['id']}"):
                        st.session_state.selected_patient = patient["id"]
                        st.rerun()

    else:

        patient_id = st.session_state.selected_patient

        try:
            result = (
                supabase
                .schema("public")
                .table("patients")
                .select("*")
                .eq("id", patient_id)
                .execute()
            )

        except Exception as e:
            st.error(f"Patient fetch error: {e}")
            st.stop()

        if not result.data:
            st.error("Patient not found")
            st.stop()

        patient = result.data[0]

        st.subheader(f"Patient: {patient['name']}")

        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Gender:** {patient['gender']}")
        st.write(f"**Phone:** {patient['phone']}")

        if st.button("⬅ Back to Patient List"):
            st.session_state.selected_patient = None
            st.rerun()

        st.divider()

        # ---------------- ADD VISIT ----------------

        st.markdown("## Add Visit")

        complaint = st.text_area("Complaint")
        diagnosis = st.text_area("Diagnosis")
        investigations = st.text_area("Investigations")
        treatment = st.text_area("Treatment")
        notes = st.text_area("Notes")

        if st.button("Save Visit"):

            try:
                supabase.schema("public").table("visits").insert({
                    "patient_id": patient_id,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "complaint": complaint,
                    "diagnosis": diagnosis,
                    "investigations": investigations,
                    "treatment": treatment,
                    "notes": notes
                }).execute()

                st.success("Visit Saved Successfully!")

            except Exception as e:
                st.error(f"Visit insert error: {e}")

        st.divider()

        # ---------------- VISIT HISTORY ----------------

        st.markdown("## Visit History")

        try:
            visits = (
                supabase
                .schema("public")
                .table("visits")
                .select("*")
                .eq("patient_id", patient_id)
                .order("date", desc=True)
                .execute()
                .data
            )

        except Exception as e:
            st.error(f"Visit fetch error: {e}")
            visits = []

        if not visits:
            st.info("No visits recorded yet.")
        else:
            for visit in visits:

                with st.expander(f"📅 {visit['date']}"):

                    st.write("**Complaint:**", visit["complaint"])
                    st.write("**Diagnosis:**", visit["diagnosis"])
                    st.write("**Investigations:**", visit["investigations"])
                    st.write("**Treatment:**", visit["treatment"])
                    st.write("**Notes:**", visit["notes"])