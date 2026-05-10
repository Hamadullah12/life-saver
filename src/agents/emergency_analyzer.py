import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior medical emergency specialist with expertise in blood transfusion. Analyze the patient emergency and return ONLY a raw JSON object with no markdown and no explanation with these exact keys:
- urgency_score: integer from 1 to 10 where 10 is most critical
- risk_level: one of "low", "moderate", "critical"
- compatible_blood_types: list of blood types compatible for this patient following real medical compatibility rules. Example: O- can donate to everyone. B+ can receive from B+, B-, O+, O-
- time_sensitivity: one of "within 30 minutes", "within 1 hour", "within 3 hours", "within 24 hours"
- recommended_units: integer of how many units are realistically needed based on urgency
- emergency_summary: 2-3 sentences describing the situation clearly for medical staff and donors
- donor_appeal_message: one powerful emotional sentence that can be sent to donors to motivate them to come forward immediately. Make it human and urgent but not panic-inducing.
- estimated_time_without_blood_minutes: integer showing how long the patient can safely wait"""


def analyze_emergency(patient_input: dict) -> dict:
    """Analyze a patient emergency using GPT-4o-mini and return structured medical assessment."""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_message = (
        f"Patient Emergency Details:\n"
        f"- Blood Type: {patient_input['blood_type']}\n"
        f"- Hospital: {patient_input['hospital_name']}\n"
        f"- City: {patient_input['city']}\n"
        f"- Units Needed: {patient_input['units_needed']}\n"
        f"- Urgency Level: {patient_input['urgency_level']}\n"
        f"- Contact Number: {patient_input['contact_number']}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )

        raw_content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw_content.startswith("```"):
            raw_content = raw_content.split("\n", 1)[1]  # remove opening ```json or ```
        if raw_content.endswith("```"):
            raw_content = raw_content.rsplit("```", 1)[0]  # remove closing ```
        raw_content = raw_content.strip()

        result = json.loads(raw_content)

        print(f"Emergency analyzed. Urgency score: {result['urgency_score']}/10")

        return result

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse emergency analysis response as JSON. "
            f"Raw response: {raw_content}\nError: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Emergency analysis failed: {e}")
