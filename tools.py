from typing import Any, Dict

from langchain_core.tools import tool
from pydantic import BaseModel



class UserDetails(BaseModel):
    user_id: int
    name: str
    status: str 
    phone: str
    db: str
    role: int



@tool
def validate_phone(phone: str) -> Dict[str, Any]:
    """Calculates the area of a rectangle given length and width."""

    user_data = {
        "user_id": 123,
        "name": "Jane Doe",
        "roles": int,
        "status": "active",
        "phone": 123456789,
        "db": "users_db"
    }

    return user_data

@tool
def get_current_weather(location: str) -> str:
    """Fetch current weather for a specific location."""
    # Placeholder for actual API call
    return f"The weather in {location} is 72°F and sunny."

# Export a list of tools for the agent to use
tools_list = [validate_phone, get_current_weather]