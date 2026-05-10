import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a blood donor matching specialist. Based on the emergency assessment provided, generate a realistic ranked list of donor profiles available in the given city and return ONLY a raw JSON array with no markdown and no explanation.
The array must contain exactly 6 donor objects.
Each donor object must have these exact keys:
- donor_id: a unique string like "DONOR-001"
- name: a realistic Pakistani name
- blood_type: must be one of the compatible_blood_types from the emergency assessment
- age: integer between 18 and 55
- city: same city as the emergency
- area: a real neighborhood in that city
- distance_km: realistic float distance from hospital
- phone: realistic Pakistani format e.g. 0312-1234567
- email: a realistic email address
- is_available: boolean true or false
- last_donated_months_ago: integer minimum 3 months
- volunteer_or_paid: one of "volunteer", "paid"
- estimated_arrival_minutes: integer realistic travel time
- match_score: integer from 1 to 100
- why_best_match: one sentence explaining this donor rank
- donor_status: one of "Active Donor", "New Donor", "Occasional Donor"
- total_donations_lifetime: integer number of times they have donated before"""


def match_donors(emergency: dict, city: str) -> list:
    """Match compatible donors based on emergency assessment and city."""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_message = (
        f"Emergency Assessment:\n"
        f"{json.dumps(emergency, indent=2)}\n\n"
        f"City: {city}\n\n"
        f"Find exactly 6 compatible donors in {city} ranked by best match."
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

        donors = json.loads(raw_content)

        # Validate exactly 6 donors
        if not isinstance(donors, list) or len(donors) != 6:
            raise ValueError(
                f"Expected exactly 6 donors, but got {len(donors) if isinstance(donors, list) else 'non-list response'}."
            )

        # Sort by match_score descending
        donors.sort(key=lambda d: d.get("match_score", 0), reverse=True)

        print(f"Donor matching complete. {len(donors)} donors found in {city}.")

        return donors

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse donor matching response as JSON. "
            f"Raw response: {raw_content}\nError: {e}"
        )
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Donor matching failed: {e}")
