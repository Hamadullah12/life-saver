import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a blood donation outreach coordinator. Using the emergency details and matched donors, create a complete contact and outreach action plan and return ONLY a raw JSON object with no markdown and no explanation with these exact keys:
- total_donors_to_contact: integer
- estimated_time_to_secure_blood_minutes: integer
- outreach_strategy: one of "immediate phone calls", "simultaneous notification", "sequential contact"
- contact_steps: a list of step objects each containing:
  - step_number: integer
  - action: short title e.g. "Call Top Matched Donor"
  - donor_name: which donor this step targets
  - donor_phone: their phone number
  - donor_email: their email
  - contact_method: one of "phone call", "SMS", "email", "app notification"
  - message_to_send: the exact message to send to this donor. Must include the donor_appeal_message, hospital name, and blood type. Make it personal and urgent.
  - time_slot_minutes: integer time for this step
  - backup_action: what to do if donor does not respond
- notification_message_for_area: a broadcast message to send to ALL donors in the city. Must include blood type, hospital name, and a strong call to action
- hospital_preparation_checklist: list of 4 specific things the hospital blood bank must prepare before donor arrives"""


def plan_outreach(emergency: dict, donors: list, hospital_name: str) -> dict:
    """Create a complete contact and outreach action plan for matched donors."""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Build user message with emergency summary, top 3 donors, and hospital
    top_donors = donors[:3]
    top_donors_summary = "\n".join(
        f"  {i+1}. {d.get('name')} | Blood: {d.get('blood_type')} | "
        f"Phone: {d.get('phone')} | Email: {d.get('email')} | "
        f"Area: {d.get('area')} | Match Score: {d.get('match_score')}"
        for i, d in enumerate(top_donors)
    )

    user_message = (
        f"Emergency Summary:\n{emergency.get('emergency_summary', '')}\n\n"
        f"Donor Appeal Message:\n{emergency.get('donor_appeal_message', '')}\n\n"
        f"Blood Type Needed: {emergency.get('compatible_blood_types', [])}\n"
        f"Urgency Score: {emergency.get('urgency_score', 'N/A')}/10\n"
        f"Time Sensitivity: {emergency.get('time_sensitivity', 'N/A')}\n\n"
        f"Hospital: {hospital_name}\n\n"
        f"Top 3 Matched Donors:\n{top_donors_summary}\n\n"
        f"Create a detailed outreach plan to contact these donors and secure blood."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
        )

        raw_content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw_content.startswith("```"):
            raw_content = raw_content.split("\n", 1)[1]
        if raw_content.endswith("```"):
            raw_content = raw_content.rsplit("```", 1)[0]
        raw_content = raw_content.strip()

        result = json.loads(raw_content)

        # Validate contact_steps is not empty
        contact_steps = result.get("contact_steps", [])
        if not contact_steps:
            raise ValueError("Outreach plan returned empty contact_steps.")

        print(f"Outreach plan ready. {len(contact_steps)} contact steps created.")

        return result

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse outreach plan response as JSON. "
            f"Raw response: {raw_content}\nError: {e}"
        )
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Outreach planning failed: {e}")
