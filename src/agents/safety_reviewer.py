import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a senior patient safety officer and blood bank compliance specialist. Review the outreach plan and emergency details for safety, compliance, and completeness, then return ONLY a raw JSON object with no markdown and no explanation with these exact keys:
- clearance_status: one of "GO — Execute Immediately", "GO WITH CAUTION — Review Warnings First", "HOLD — Critical Issues Found"
- overall_review: 2-3 sentences on whether this plan will successfully get blood to the patient in time
- safety_warnings: list of specific risks found. Return empty list if none found.
- contact_steps: the same contact_steps list from the outreach plan but with one extra key per step:
  - safety_checkpoint: a specific verifiable confirmation before this step is marked complete. Must be concrete and clinical, not vague. Example: "Confirm donor has not donated in the last 3 months by asking directly before proceeding" Not "Verify donor details."
- final_recommendation: one clear sentence telling the medical team exactly what to do right now
- success_probability_percent: integer from 0 to 100
- if_plan_fails_backup: specific backup plan in 2-3 sentences if all donors are unavailable"""


def review_and_confirm(outreach_plan: dict, emergency: dict) -> dict:
    """Review outreach plan and emergency for safety, compliance, and completeness."""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_message = (
        f"=== EMERGENCY ASSESSMENT ===\n"
        f"{json.dumps(emergency, indent=2)}\n\n"
        f"=== OUTREACH PLAN ===\n"
        f"{json.dumps(outreach_plan, indent=2)}\n\n"
        f"Review this plan for safety, compliance, and completeness. "
        f"Add a safety_checkpoint to each contact step."
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
            raw_content = raw_content.split("\n", 1)[1]
        if raw_content.endswith("```"):
            raw_content = raw_content.rsplit("```", 1)[0]
        raw_content = raw_content.strip()

        result = json.loads(raw_content)

        print(f"Safety review complete. Status: {result['clearance_status']}")

        return result

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse safety review response as JSON. "
            f"Raw response: {raw_content}\nError: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"Safety review failed: {e}")
