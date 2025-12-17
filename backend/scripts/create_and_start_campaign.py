#!/usr/bin/env python3
"""Script to create and start a campaign (for Docker use)."""
import sys
import os
import requests

# When running inside Docker, use the service name
# When running locally, use localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


def create_campaign(agent_type: str = "sms", lead_count: int = 5):
    """Create a test campaign."""
    print(f"\n🚀 Creating test campaign...")
    print(f"   Agent Type: {agent_type}")
    print(f"   Lead Count: {lead_count}")
    
    payload = {
        "name": f"Test Campaign - {agent_type.upper()}",
        "description": f"Testing {agent_type} agent with {lead_count} leads",
        "agent_type": agent_type,
        "sms_system_prompt": "You are a friendly sales assistant. Generate a brief, professional SMS message to introduce our product.",
        "sms_temperature": 70,
        "lead_count": lead_count
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/campaigns/", json=payload)
        response.raise_for_status()
        campaign = response.json()
        campaign_id = campaign['id']
        print(f"✅ Campaign created: ID {campaign_id}")
        return campaign_id
    except Exception as e:
        print(f"❌ Error creating campaign: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None


def start_campaign(campaign_id: int):
    """Start campaign processing."""
    print(f"\n▶️  Starting campaign {campaign_id}...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/campaigns/{campaign_id}/start")
        response.raise_for_status()
        result = response.json()
        print(f"✅ Campaign started!")
        if 'job_id' in result:
            print(f"   Job ID: {result.get('job_id')}")
        return True
    except Exception as e:
        print(f"❌ Error starting campaign: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return False


def main():
    """Main function."""
    agent_type = sys.argv[1] if len(sys.argv) > 1 else "sms"
    lead_count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    if agent_type not in ['sms', 'voice', 'both']:
        print("❌ Invalid agent_type. Must be: sms, voice, or both")
        sys.exit(1)
    
    print("=" * 60)
    print("🧪 FastAPI LangGraph POC - Create & Start Campaign")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    
    # Create campaign
    campaign_id = create_campaign(agent_type, lead_count)
    if not campaign_id:
        sys.exit(1)
    
    # Start campaign
    if not start_campaign(campaign_id):
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✨ Campaign created and started!")
    print(f"   Campaign ID: {campaign_id}")
    print(f"   View in frontend: http://localhost:3000/campaigns/{campaign_id}")
    print(f"   API endpoint: {API_BASE_URL}/campaigns/{campaign_id}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()



