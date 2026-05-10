import os
import sys
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("ERROR: OPENAI_API_KEY missing. Add it to your .env file.")

print("Life Saver is ready.\n")

# Add src to path so agent imports work when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from agents.emergency_analyzer import analyze_emergency
from agents.donor_matcher import match_donors
from agents.outreach_planner import plan_outreach
from agents.safety_reviewer import review_and_confirm

# Hardcoded test patient
test_patient = {
    "blood_type": "B+",
    "hospital_name": "Hayatabad Medical Complex",
    "city": "Peshawar",
    "units_needed": "2",
    "urgency_level": "critical",
    "contact_number": "0312-1234567",
}

try:
    # ── Step 1: Analyze Emergency ──────────────────────────────
    print("=" * 55)
    print("  STEP 1: ANALYZING EMERGENCY")
    print("=" * 55)
    emergency = analyze_emergency(test_patient)
    print(f"  Urgency Score      : {emergency['urgency_score']}/10")
    print(f"  Risk Level         : {emergency['risk_level']}")
    print(f"  Compatible Types   : {emergency['compatible_blood_types']}")
    print(f"  Time Without Blood : {emergency['estimated_time_without_blood_minutes']} minutes")
    print()

    # ── Step 2: Match Donors ───────────────────────────────────
    print("=" * 55)
    print("  STEP 2: MATCHING DONORS")
    print("=" * 55)
    donors = match_donors(emergency, test_patient["city"])
    print(f"  Donors Found       : {len(donors)}")
    top_donor = donors[0]
    print(f"  Top Donor Name     : {top_donor['name']}")
    print(f"  Top Donor Blood    : {top_donor['blood_type']}")
    print(f"  Top Donor Score    : {top_donor['match_score']}/100")
    print()

    # ── Step 3: Plan Outreach ──────────────────────────────────
    print("=" * 55)
    print("  STEP 3: PLANNING OUTREACH")
    print("=" * 55)
    outreach_plan = plan_outreach(emergency, donors, test_patient["hospital_name"])
    print(f"  Outreach Strategy  : {outreach_plan['outreach_strategy']}")
    print(f"  Contact Steps      : {len(outreach_plan['contact_steps'])}")
    print()

    # ── Step 4: Safety Review ──────────────────────────────────
    print("=" * 55)
    print("  STEP 4: SAFETY REVIEW")
    print("=" * 55)
    review = review_and_confirm(outreach_plan, emergency)
    print(f"  Clearance Status   : {review['clearance_status']}")
    print(f"  Success Probability: {review['success_probability_percent']}%")
    print(f"  Recommendation     : {review['final_recommendation']}")
    print()

    # ── Pipeline Complete ──────────────────────────────────────
    print("=" * 55)
    print("  Life Saver pipeline complete. Patient can be saved.")
    print("=" * 55)

except Exception as e:
    print(f"\nPIPELINE ERROR: {e}")
    sys.exit(1)
