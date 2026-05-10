# Life Saver

A multi-agent AI system for emergency response coordination.

## Setup

1. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```
   cp .env.example .env
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/main.py
   ```

## Project Structure

```
life-saver/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── emergency_analyzer.py
│   │   ├── donor_matcher.py
│   │   ├── outreach_planner.py
│   │   └── safety_reviewer.py
│   ├── main.py
│   └── app.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

## Agents

- **Emergency Analyzer** - Analyzes emergency situations
- **Donor Matcher** - Matches donors with recipients
- **Outreach Planner** - Plans outreach campaigns
- **Safety Reviewer** - Reviews safety protocols
