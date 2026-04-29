"""
brain.py
The AI brain — reads plain English commands and converts them
into precise robot action plans with 3D coordinates.

Uses Groq's free API (LLaMA 3.3 70B model).
Groq is fast: responses typically arrive in under 1 second.
"""
import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()   # Reads GROQ_API_KEY from your .env file


class RobotBrain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError(
                "❌ GROQ_API_KEY missing.\n"
                "   1. Open the file called .env\n"
                "   2. Replace 'your_groq_api_key_here' with your real key from console.groq.com"
            )
        self.client = Groq(api_key=api_key)
        # Check console.groq.com/docs/models if this name stops working
        self.model  = "llama-3.3-70b-versatile"
        print(f"✅ AI Brain connected (model: {self.model})")

    def parse_command(self, user_command: str, scene_description: str):
        """
        Converts a plain English command into a structured robot action plan.

        Args:
            user_command      : e.g. "pick up the red cube and place it left of blue"
            scene_description : text description of all current objects and positions

        Returns:
            dict: action plan with steps and coordinates
            None: if something went wrong
        """

        system_prompt = """You are the AI brain of a 6-DOF robotic arm in a 3D physics simulation.

Your only job is to convert natural language commands into precise robot action plans.

=== COORDINATE SYSTEM ===
- X axis: positive = to the RIGHT of the robot
- Y axis: positive = FORWARD (away from the robot)
- Z axis: positive = UP
- Robot base is fixed at [0, 0, 0]
- Objects rest on the floor at z ≈ 0.03 to 0.05
- Robot arm can comfortably reach: x from -0.6 to 0.6, y from 0.1 to 0.7, z from 0.0 to 0.8
- "left of X"  → lower X coordinate than X's position
- "right of X" → higher X coordinate than X's position
- "in front of X" → lower Y than X's position
- "behind X"   → higher Y than X's position

=== OUTPUT FORMAT ===
Respond with ONLY a valid JSON object — no explanation outside the JSON, no markdown.

{
  "action": "pick_and_place",
  "steps": [
    {
      "step": 1,
      "description": "Move above the red cube",
      "target_object": "red_cube",
      "position": [0.40, 0.00, 0.18],
      "is_pickup": true,
      "is_place": false
    },
    {
      "step": 2,
      "description": "Place red cube left of blue cube",
      "target_object": "red_cube",
      "position": [0.10, 0.22, 0.15],
      "is_pickup": false,
      "is_place": true
    }
  ],
  "explanation": "I will pick up the red cube and move it to the left of the blue cube."
}

action values:
  "pick_and_place" → moving objects
  "move_to"        → just moving the arm tip to a position (no object)
  "home"           → return arm to resting position
  "error"          → command impossible or unclear

If the command is unclear, action="error" and explain in explanation field.
Think carefully. Calculate exact coordinates based on the object positions given."""

        user_message = (
            f"Current scene:\n{scene_description}\n\n"
            f'Command: "{user_command}"\n\n'
            "Output ONLY the JSON action plan:"
        )

        try:
            print(f"🧠 Thinking: '{user_command}'...")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",  "content": system_prompt},
                    {"role": "user",    "content": user_message}
                ],
                temperature=0.1,    # Low = consistent, predictable behavior
                max_tokens=600
            )

            raw = response.choices[0].message.content.strip()

            # Strip markdown code fences if model accidentally adds them
            if raw.startswith("```"):
                lines = raw.split("\n")
                raw   = "\n".join(lines[1:-1]) if len(lines) > 2 else raw

            plan = json.loads(raw)
            print(f"💡 Plan: {plan.get('explanation', '(no explanation)')}")
            return plan

        except json.JSONDecodeError:
            print(f"❌ Brain returned invalid JSON. Raw output:\n{raw[:300]}")
            return None
        except Exception as e:
            print(f"❌ Brain error: {e}")
            return None