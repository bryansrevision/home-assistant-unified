"""AI intelligence module for natural language processing and command interpretation."""

import logging
import re
from typing import Any

from openai import OpenAI

from home_automation.core.config import Config

logger = logging.getLogger(__name__)


class AIIntelligence:
    """AI intelligence for natural language processing and automation decisions."""

    def __init__(self, config: Config):
        """Initialize AI intelligence."""
        self.config = config

        # Set up OpenAI if API key is provided
        if config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.use_openai = True
        else:
            self.client = None
            self.use_openai = False
            logger.warning("No OpenAI API key provided, using basic pattern matching")

        # Basic command patterns for fallback
        self.command_patterns = {
            r"turn on (?:the )?(.+)": {"action": "turn_on", "target": "$1"},
            r"turn off (?:the )?(.+)": {"action": "turn_off", "target": "$1"},
            r"switch on (?:the )?(.+)": {"action": "turn_on", "target": "$1"},
            r"switch off (?:the )?(.+)": {"action": "turn_off", "target": "$1"},
            r"set (?:the )?(.+?) (?:to )?(\d+)(?:\s?degrees?)?": {"action": "set_temperature", "target": "$1", "temperature": "$2"},
            r"what(?:'s| is) the status of (?:the )?(.+)": {"action": "get_status", "target": "$1"},
            r"how(?:'s| is) (?:the )?(.+) doing": {"action": "get_status", "target": "$1"},
        }

    def interpret_command(self, command: str) -> dict[str, Any] | None:
        """Interpret a natural language command."""
        if self.use_openai:
            return self._interpret_with_openai(command)
        else:
            return self._interpret_with_patterns(command)

    def _interpret_with_openai(self, command: str) -> dict[str, Any] | None:
        """Interpret command using OpenAI."""
        try:
            prompt = f"""
You are a home automation AI assistant. Interpret the following command and extract:
1. action (turn_on, turn_off, set_temperature, get_status, etc.)
2. target (device name)
3. parameters (if any, like temperature values)

Command: "{command}"

Respond in this exact JSON format:
{{"action": "action_name", "target": "device_name", "parameters": {{"key": "value"}}}}

If you cannot interpret the command, respond with: {{"error": "cannot_interpret"}}
"""

            response = self.client.chat.completions.create(
                model=self.config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.AI_TEMPERATURE,
                max_tokens=self.config.AI_MAX_TOKENS
            )

            content = response.choices[0].message.content.strip()

            # Try to parse the JSON response
            import json
            try:
                result = json.loads(content)
                if "error" in result:
                    return None
                return result
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI response: {content}")
                return self._interpret_with_patterns(command)

        except Exception as e:
            logger.error(f"OpenAI interpretation failed: {e}")
            return self._interpret_with_patterns(command)

    def _interpret_with_patterns(self, command: str) -> dict[str, Any] | None:
        """Interpret command using regex patterns."""
        command_lower = command.lower().strip()

        for pattern, template in self.command_patterns.items():
            match = re.search(pattern, command_lower)
            if match:
                result = {}

                for key, value in template.items():
                    if value.startswith("$"):
                        # Replace with capture group
                        group_num = int(value[1:])
                        if group_num <= len(match.groups()):
                            result[key] = match.group(group_num).strip()
                    else:
                        result[key] = value

                # Convert temperature to float if present
                if "temperature" in result:
                    try:
                        result["parameters"] = {"temperature": float(result.pop("temperature"))}
                    except ValueError:
                        continue

                return result

        return None

    def generate_response(self, context: dict[str, Any]) -> str:
        """Generate a natural language response based on context."""
        if self.use_openai:
            return self._generate_response_with_openai(context)
        else:
            return self._generate_basic_response(context)

    def _generate_response_with_openai(self, context: dict[str, Any]) -> str:
        """Generate response using OpenAI."""
        try:
            prompt = f"""
You are a helpful home automation assistant. Based on the following context, 
generate a natural, friendly response to the user.

Context: {context}

Generate a brief, natural response (1-2 sentences max).
"""

            response = self.client.chat.completions.create(
                model=self.config.AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.AI_TEMPERATURE,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI response generation failed: {e}")
            return self._generate_basic_response(context)

    def _generate_basic_response(self, context: dict[str, Any]) -> str:
        """Generate a basic response without AI."""
        if context.get("success"):
            action = context.get("interpretation", {}).get("action", "action")
            target = context.get("interpretation", {}).get("target", "device")

            if action == "turn_on":
                return f"I've turned on the {target}."
            elif action == "turn_off":
                return f"I've turned off the {target}."
            elif action == "set_temperature":
                temp = context.get("interpretation", {}).get("parameters", {}).get("temperature")
                return f"I've set the {target} to {temp} degrees."
            elif action == "get_status":
                status = context.get("result", {}).get("status", "unknown")
                return f"The {target} is currently {status}."
            else:
                return f"I've completed the {action} for {target}."
        else:
            return "I'm sorry, I couldn't complete that request."

    def analyze_sensor_data(self, sensor_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze sensor data and provide insights."""
        if not sensor_data:
            return {"insights": [], "recommendations": []}

        insights = []
        recommendations = []

        # Basic analysis
        for data_point in sensor_data:
            sensor_type = data_point.get("sensor_type", "").lower()
            value = data_point.get("value", 0)

            if sensor_type == "temperature":
                if value > 25:
                    insights.append(f"Temperature is high at {value}°C")
                    recommendations.append("Consider turning on air conditioning")
                elif value < 18:
                    insights.append(f"Temperature is low at {value}°C")
                    recommendations.append("Consider turning on heating")

            elif sensor_type == "humidity":
                if value > 60:
                    insights.append(f"Humidity is high at {value}%")
                    recommendations.append("Consider running dehumidifier")
                elif value < 30:
                    insights.append(f"Humidity is low at {value}%")
                    recommendations.append("Consider running humidifier")

        return {
            "insights": insights,
            "recommendations": recommendations,
            "data_points_analyzed": len(sensor_data)
        }
