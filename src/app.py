import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.emergency_analyzer import analyze_emergency
from agents.donor_matcher import match_donors
from agents.outreach_planner import plan_outreach
from agents.safety_reviewer import review_and_confirm

st.set_page_config(page_title="Life Saver", layout="wide", page_icon="🩸")

# ── Load Secrets for Cloud Deployment ──────────────────────
# This ensures agents can see keys set in Streamlit Cloud Secrets
for key in ["OPENAI_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", 
            "TWILIO_PHONE_NUMBER", "SENDGRID_API_KEY", "GOOGLE_MAPS_API_KEY"]:
    if key in st.secrets:
        os.environ[key] = st.secrets[key]

# ── Minimalist CSS ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Clean, calm palette */
.hero { text-align: center; padding: 3rem 1rem 1rem; }
.hero h1 { font-size: 2.8rem; font-weight: 700; letter-spacing: -1px; margin: 0; }
.hero p { color: #999; font-size: 1.05rem; margin-top: 0.3rem; }
.hero .accent { color: #dc3545; font-weight: 500; font-size: 0.9rem; }

/* Stat pills */
.stats-row { display: flex; gap: 1rem; justify-content: center; margin: 2rem 0; }
.stat-pill { background: #111; border: 1px solid #222; border-radius: 12px;
    padding: 1rem 2rem; text-align: center; flex: 1; max-width: 200px; }
.stat-pill .num { font-size: 1.5rem; font-weight: 700; color: #fff; }
.stat-pill .lbl { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }

/* Cards */
.clean-card { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 12px;
    padding: 1.25rem 1.5rem; margin-bottom: 0.75rem; }
.clean-card h4 { margin: 0 0 0.5rem 0; font-weight: 600; font-size: 0.95rem; }
.clean-card p { margin: 0; color: #aaa; font-size: 0.88rem; line-height: 1.5; }

/* Donor row */
.donor-row { background: #0d0d0d; border: 1px solid #1a1a1a; border-radius: 10px;
    padding: 1rem 1.25rem; margin-bottom: 0.5rem; display: flex;
    justify-content: space-between; align-items: center; }
.donor-row .name { font-weight: 600; font-size: 0.95rem; }
.donor-row .meta { color: #888; font-size: 0.8rem; }
.donor-row .score { font-weight: 700; color: #dc3545; font-size: 1.1rem; }

/* Status badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.5px; }
.badge-go { background: #0d2818; color: #4ade80; }
.badge-caution { background: #2d1f00; color: #fbbf24; }
.badge-hold { background: #2d0a0a; color: #f87171; }
.badge-avail { background: #0d2818; color: #4ade80; }
.badge-unavail { background: #1a1a1a; color: #888; }

/* Footer */
.ft { text-align: center; color: #444; font-size: 0.72rem; margin-top: 4rem;
    padding: 1rem 0; border-top: 1px solid #1a1a1a; }

/* Reduce button visual weight */
div.stButton > button { border-radius: 10px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────
for k in ["current_dashboard", "patient_result", "donor_profile"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ── Sidebar — minimal ─────────────────────────────────────
with st.sidebar:
    st.markdown("### 🩸 Life Saver")
    st.caption("Faster blood matching saves lives")
    st.divider()
    st.caption("📍 Serving Peshawar")
    st.caption("🔜 Expanding nationwide")
    st.divider()
    if st.session_state.current_dashboard:
        label = "Patient" if st.session_state.current_dashboard == "patient" else "Donor"
        st.markdown(f"**Dashboard:** {label}")
    if st.button("← Back to Home", use_container_width=True):
        st.session_state.current_dashboard = None
        st.rerun()

def footer():
    st.markdown('<div class="ft">Life Saver — National AI Hackathon · Peshawar · Every second counts</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  HOMEPAGE — clean, two choices only
# ══════════════════════════════════════════════════════════
if st.session_state.current_dashboard is None:

    st.markdown("""
    <div class="hero">
        <h1>🩸 Life Saver</h1>
        <p>Find the right blood donor in minutes, not hours.</p>
        <p class="accent">Every minute counts. AI-powered matching starts instantly.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("🚨  I Need Blood", type="primary", use_container_width=True, key="go_patient"):
            st.session_state.current_dashboard = "patient"
            st.rerun()
        st.caption("For patients & hospital staff")
    with col2:
        if st.button("🩸  I Am a Donor", use_container_width=True, key="go_donor"):
            st.session_state.current_dashboard = "donor"
            st.rerun()
        st.caption("Register or view your profile")

    st.markdown("""
    <div class="stats-row">
        <div class="stat-pill"><div class="num">1,247</div><div class="lbl">Donors</div></div>
        <div class="stat-pill"><div class="num">23</div><div class="lbl">Hospitals</div></div>
        <div class="stat-pill"><div class="num">389</div><div class="lbl">Lives Saved</div></div>
    </div>
    """, unsafe_allow_html=True)

    footer()


# ══════════════════════════════════════════════════════════
#  PATIENT DASHBOARD — calm, focused, minimal
# ══════════════════════════════════════════════════════════
elif st.session_state.current_dashboard == "patient":

    st.markdown("### 🚨 Emergency Blood Request")
    st.caption("Enter patient details. AI finds compatible donors instantly.")

    # ── Input Form ─────────────────────────────────────────
    with st.form("patient_form"):
        c1, c2 = st.columns(2)
        with c1:
            blood_type = st.selectbox("Blood Type", ["A+","A-","B+","B-","AB+","AB-","O+","O-"])
        with c2:
            urgency = st.selectbox("Urgency", ["critical","urgent","scheduled"])
        hospital = st.text_input("Hospital", placeholder="Hayatabad Medical Complex")
        city = st.text_input("City", placeholder="Peshawar")
        c3, c4 = st.columns(2)
        with c3:
            units = st.number_input("Units Needed", 1, 10, 1)
        with c4:
            phone = st.text_input("Contact Number", placeholder="0312-1234567")
        go = st.form_submit_button("Find Donors →", type="primary")

    if go:
        if not hospital.strip() or not city.strip() or not phone.strip():
            st.error("Please fill all fields.")
            st.stop()

        patient_input = {
            "blood_type": blood_type, "hospital_name": hospital,
            "city": city, "units_needed": str(units),
            "urgency_level": urgency, "contact_number": phone,
        }
        try:
            with st.spinner("Analyzing emergency…"):
                emergency = analyze_emergency(patient_input)
            with st.spinner(f"Matching donors in {city}…"):
                donors = match_donors(emergency, city)
            with st.spinner("Building outreach plan…"):
                outreach = plan_outreach(emergency, donors, hospital)
            with st.spinner("Safety review…"):
                review = review_and_confirm(outreach, emergency)

            st.session_state.patient_result = {
                "emergency": emergency, "donors": donors,
                "outreach": outreach, "review": review,
            }
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    # ── Results ────────────────────────────────────────────
    if st.session_state.patient_result:
        r = st.session_state.patient_result
        em = r["emergency"]
        donors = r["donors"]
        outreach = r["outreach"]
        review = r["review"]

        st.divider()

        # Status banner — single clear line
        status = review.get("clearance_status", "")
        if "Execute Immediately" in status:
            st.success(f"✅ DONORS FOUND — EXECUTE NOW  ·  {review.get('success_probability_percent',0)}% chance of success")
        elif "CAUTION" in status:
            st.warning(f"⚠️ PROCEED WITH CAUTION  ·  {review.get('success_probability_percent',0)}% chance")
        else:
            st.error(f"🛑 HOLD — PHYSICIAN REVIEW NEEDED  ·  {review.get('success_probability_percent',0)}% chance")

        st.markdown(f"*{review.get('final_recommendation','')}*")

        # ── Quick Summary Row ──────────────────────────────
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Urgency", f"{em.get('urgency_score','?')}/10")
        q2.metric("Risk", em.get("risk_level","?").title())
        q3.metric("Time Window", em.get("time_sensitivity","?"))
        q4.metric("Safe Wait", f"{em.get('estimated_time_without_blood_minutes','?')} min")

        # ── Compatible types ───────────────────────────────
        compat = ", ".join(em.get("compatible_blood_types", []))
        st.caption(f"Compatible blood types: **{compat}**")

        # ── Emergency Summary (collapsed by default context) ─
        with st.expander("📋 Emergency Details"):
            st.markdown(em.get("emergency_summary", ""))
            st.markdown(f"*\"{em.get('donor_appeal_message','')}\"*")

        # ── Safety Warnings ────────────────────────────────
        warnings = review.get("safety_warnings", [])
        if warnings:
            with st.expander(f"⚠️ Safety Warnings ({len(warnings)})"):
                for w in warnings:
                    st.warning(w)

        # ── Matched Donors — clean list ────────────────────
        st.markdown("#### Matched Donors")
        top = donors[0]
        st.caption(f"{len(donors)} donors found · Top match: {top['name']} at {top['match_score']}%")

        for d in donors:
            avail = "✅" if d.get("is_available") else "⏳"
            with st.expander(f"{avail}  {d['name']}  ·  {d['blood_type']}  ·  {d.get('area','')}  ·  {d['match_score']}% match  ·  {d.get('estimated_arrival_minutes','')} min away"):
                lc, rc = st.columns(2)
                with lc:
                    st.markdown(f"**Phone:** {d.get('phone','')}")
                    st.markdown(f"**Email:** {d.get('email','')}")
                    st.markdown(f"**Area:** {d.get('area','')} ({d.get('distance_km','')} km)")
                with rc:
                    st.markdown(f"**Last Donated:** {d.get('last_donated_months_ago','')} months ago")
                    st.markdown(f"**Lifetime Donations:** {d.get('total_donations_lifetime','')}")
                    st.markdown(f"**Type:** {d.get('volunteer_or_paid','')}")
                st.caption(d.get("why_best_match",""))

        # ── Contact Plan — streamlined ─────────────────────
        st.markdown("#### Contact Plan")
        st.caption(f"Strategy: {outreach.get('outreach_strategy','')} · Est. {outreach.get('estimated_time_to_secure_blood_minutes','')} min to secure blood")

        review_steps = review.get("contact_steps", outreach.get("contact_steps", []))
        for step in review_steps:
            with st.expander(f"Step {step.get('step_number','')} → {step.get('donor_name','')} via {step.get('contact_method','')}"):
                st.info(step.get("message_to_send",""))
                if step.get("safety_checkpoint"):
                    st.caption(f"🛡️ Checkpoint: {step['safety_checkpoint']}")
                st.caption(f"Backup: {step.get('backup_action','')}")

        # ── Hospital Prep ──────────────────────────────────
        checklist = outreach.get("hospital_preparation_checklist", [])
        if checklist:
            with st.expander("🏥 Hospital Preparation"):
                for i, item in enumerate(checklist, 1):
                    st.markdown(f"{i}. {item}")

        # ── Broadcast + Backup — tucked away ───────────────
        with st.expander("📢 Broadcast Message for All Donors"):
            st.success(outreach.get("notification_message_for_area", ""))
            st.caption("Copy and send to all registered donors in your city.")

        with st.expander("🔄 Backup Plan"):
            st.warning(review.get("if_plan_fails_backup", ""))

        st.markdown("")
        if st.button("↻ New Search", type="primary"):
            st.session_state.patient_result = None
            st.rerun()

    footer()


# ══════════════════════════════════════════════════════════
#  DONOR DASHBOARD — clean tabs
# ══════════════════════════════════════════════════════════
elif st.session_state.current_dashboard == "donor":

    tab_reg, tab_profile = st.tabs(["Register", "My Profile"])

    # ── Register ───────────────────────────────────────────
    with tab_reg:
        st.markdown("### Join as a Blood Donor")
        st.caption("Register once. Get notified when someone nearby needs your blood type.")

        with st.form("donor_form"):
            a1, a2 = st.columns(2)
            with a1: d_name = st.text_input("Full Name", placeholder="Your full name")
            with a2: d_father = st.text_input("Father's Name", placeholder="For verification")
            b1, b2 = st.columns(2)
            with b1: d_blood = st.selectbox("Blood Type", ["A+","A-","B+","B-","AB+","AB-","O+","O-"], key="db")
            with b2: d_age = st.number_input("Age", 18, 60, 25)
            c1, c2 = st.columns(2)
            with c1: d_phone = st.text_input("Phone", placeholder="0312-1234567")
            with c2: d_email = st.text_input("Email", placeholder="you@email.com")
            d1, d2 = st.columns(2)
            with d1: d_city = st.text_input("City", value="Peshawar", key="dc")
            with d2: d_area = st.text_input("Area", placeholder="Hayatabad, University Town")
            e1, e2 = st.columns(2)
            with e1: d_weight = st.number_input("Weight (kg)", 50, 150, 70)
            with e2: d_type = st.selectbox("Donate As", ["Volunteer (free)", "Paid (bank rates)"])
            d_freq = st.selectbox("Frequency", ["Every 3 months","Every 6 months","Only in emergencies","Whenever needed"])
            d_medical = st.text_area("Medical Conditions", placeholder="Leave empty if none", height=68)
            chk1 = st.checkbox("I have NOT donated blood in the last 3 months")
            chk2 = st.checkbox("I agree to be contacted during emergencies")
            chk3 = st.checkbox("All information above is accurate")
            reg = st.form_submit_button("Register →", type="primary")

        if reg:
            errs = []
            if not d_name.strip(): errs.append("Name required.")
            if not d_phone.strip(): errs.append("Phone required.")
            if not d_email.strip(): errs.append("Email required.")
            if not d_city.strip(): errs.append("City required.")
            if not d_area.strip(): errs.append("Area required.")
            if not chk1: errs.append("Confirm last donation was 3+ months ago.")
            if not chk2: errs.append("Agree to emergency contact.")
            if not chk3: errs.append("Confirm accuracy.")
            if errs:
                for e in errs: st.error(e)
            else:
                st.session_state.donor_profile = {
                    "name": d_name, "father_name": d_father, "blood_type": d_blood,
                    "age": d_age, "phone": d_phone, "email": d_email, "city": d_city,
                    "area": d_area, "weight": d_weight, "donation_type": d_type,
                    "frequency": d_freq, "medical_conditions": d_medical,
                    "availability": "Available",
                }
                st.balloons()
                st.success(f"Welcome, {d_name}! You're registered as a {d_blood} donor in {d_area}, {d_city}. 🦸")

    # ── My Profile ─────────────────────────────────────────
    with tab_profile:
        if st.session_state.donor_profile:
            p = st.session_state.donor_profile

            st.markdown(f"### {p['name']}")
            st.caption(f"{p['blood_type']} donor · {p['area']}, {p['city']}")

            m1, m2, m3 = st.columns(3)
            m1.metric("Blood Type", p["blood_type"])
            m2.metric("Status", "Active ✅")
            m3.metric("Availability", p.get("availability","Available"))

            with st.expander("📋 My Details", expanded=True):
                lc, rc = st.columns(2)
                with lc:
                    st.markdown(f"**Phone:** {p['phone']}")
                    st.markdown(f"**Email:** {p['email']}")
                    st.markdown(f"**Age:** {p['age']} · **Weight:** {p['weight']} kg")
                with rc:
                    st.markdown(f"**Type:** {p['donation_type']}")
                    st.markdown(f"**Frequency:** {p['frequency']}")
                    st.markdown(f"**Medical:** {p.get('medical_conditions','None') or 'None'}")

            # Availability toggle
            avail = st.selectbox("Availability", ["Available","Unavailable","Weekends Only"],
                index=["Available","Unavailable","Weekends Only"].index(p.get("availability","Available")),
                key="avail_sel")
            if avail != p.get("availability"):
                st.session_state.donor_profile["availability"] = avail
                st.success(f"Status updated to: {avail}")

            # Simulated emergency
            st.divider()
            st.markdown("#### 🚨 Active Emergency Near You")
            st.error(f"**{p['blood_type']} needed** at Hayatabad Medical Complex, Peshawar\n\n2 units · Within 1 hour · 3.2 km from you")
            ac1, ac2 = st.columns(2)
            with ac1:
                if st.button("✅ I Can Help", type="primary", key="accept"):
                    st.success("**Go to:** Hayatabad Medical Complex Blood Bank\n\n📞 091-9217140 · Bring your CNIC · Arrive hydrated")
            with ac2:
                if st.button("❌ Can't Right Now", key="decline"):
                    st.info("No problem. We'll contact the next donor.")

            # Impact
            st.divider()
            i1, i2, i3 = st.columns(3)
            i1.metric("Donations", 0)
            i2.metric("Lives Impacted", 0)
            i3.metric("Member Since", "Today")
            st.caption("Every donation saves up to 3 lives. Thank you. 🙏")

            # Edit
            with st.expander("✏️ Edit Profile"):
                np = st.text_input("Phone", value=p["phone"], key="ep")
                ne = st.text_input("Email", value=p["email"], key="ee")
                na = st.text_input("Area", value=p["area"], key="ea")
                if st.button("Save", key="save_edit"):
                    st.session_state.donor_profile.update({"phone": np, "email": ne, "area": na})
                    st.success("Profile updated.")
        else:
            st.info("Register first to see your profile.")

    footer()
