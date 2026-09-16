import json
import os

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "user_profile.json")

def load_user_profile():
    """
    Long-term memory JSON file se user context load karta hai.
    """
    if not os.path.exists(PROFILE_PATH):
        return {
            "name": "User",
            "role": "Computer Science Student",
            "preferred_tech_stack": [],
            "known_facts": [],
            "conversation_style": "detailed, technical, and practical",
            "total_interactions": 0
        }
    
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_user_profile(profile_data):
    """
    Updated user context ko JSON file me persist karta hai.
    """
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

def increment_interaction_count():
    """
    Track karta hai ki user ne overall kitni baar chat ki hai.
    """
    profile = load_user_profile()
    profile["total_interactions"] = profile.get("total_interactions", 0) + 1
    save_user_profile(profile)

def add_user_fact(new_fact):
    """
    User ke baare me naya fact memory me append karta hai.
    """
    profile = load_user_profile()
    facts = profile.get("known_facts", [])
    if new_fact not in facts:
        facts.append(new_fact)
        profile["known_facts"] = facts
        save_user_profile(profile)

def get_profile_context_prompt():
    """
    System prompt ke andar inject karne ke liye contextual memory string banata hai.
    """
    profile = load_user_profile()
    
    context = (
        f"\n[Persistent User Memory & Cognitive Profile]\n"
        f"- Target User Role: {profile.get('role', 'Student')}\n"
        f"- Preferred Communication: {profile.get('conversation_style', 'Technical & practical')}\n"
        f"- Total Prior Interactions: {profile.get('total_interactions', 0)}\n"
    )
    
    facts = profile.get("known_facts", [])
    if facts:
        context += "- User Known Facts:\n"
        for fact in facts:
            context += f"  * {fact}\n"
            
    stack = profile.get("preferred_tech_stack", [])
    if stack:
        context += f"- User Known Tech Stack: {', '.join(stack)}\n"
        
    return context