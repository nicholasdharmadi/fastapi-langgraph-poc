#!/usr/bin/env python3
"""Test script for running a campaign with a custom voice workflow."""
import sys
import time
import requests
import json
from typing import Optional

API_BASE_URL = "http://localhost:8000/api"

def create_custom_voice_campaign(lead_count: int = 5) -> Optional[int]:
    """Create a test campaign with a custom voice workflow."""
    print(f"\n🚀 Creating custom voice workflow campaign...")
    
    # Define custom workflow: Start -> Voice Call -> End
    workflow_config = {
        "nodes": [
            {
                "id": "start",
                "type": "input",
                "data": {"label": "Start Campaign"},
                "position": {"x": 250, "y": 0}
            },
            {
                "id": "validate-1",
                "data": {"label": "Validate Lead"},
                "position": {"x": 250, "y": 100}
            },
            {
                "id": "voice-1",
                "data": {"label": "Voice Call"},
                "position": {"x": 250, "y": 200}
            },
            {
                "id": "end",
                "type": "output",
                "data": {"label": "End"},
                "position": {"x": 250, "y": 300}
            }
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "validate-1"},
            {"id": "e2", "source": "validate-1", "target": "voice-1"},
            {"id": "e3", "source": "voice-1", "target": "end"}
        ]
    }
    
    payload = {
        "name": "Custom Voice Workflow Test",
        "description": "Testing custom workflow with Voice Call node",
        "agent_type": "voice",
        "lead_count": lead_count,
        "workflow_config": workflow_config
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
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return None

def start_campaign(campaign_id: int) -> bool:
    """Start campaign processing."""
    print(f"\n▶️  Starting campaign {campaign_id}...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/campaigns/{campaign_id}/start")
        response.raise_for_status()
        result = response.json()
        print(f"✅ Campaign started: Job ID {result.get('job_id')}")
        return True
    except Exception as e:
        print(f"❌ Error starting campaign: {e}")
        return False

def monitor_campaign(campaign_id: int, max_wait: int = 300):
    """Monitor campaign progress."""
    print(f"\n📊 Monitoring campaign {campaign_id}...")
    
    start_time = time.time()
    last_status = None
    
    try:
        while True:
            if time.time() - start_time > max_wait:
                print(f"\n⏱️  Max wait time ({max_wait}s) exceeded")
                break
            
            try:
                response = requests.get(f"{API_BASE_URL}/campaigns/{campaign_id}")
                response.raise_for_status()
                campaign = response.json()
                
                status = campaign['status']
                stats = campaign.get('stats', {})
                
                if status != last_status:
                    print(f"\n📌 Status: {status}")
                    last_status = status
                
                # Print progress
                total = stats.get('total_leads', 0)
                completed = stats.get('completed', 0)
                failed = stats.get('failed', 0)
                processing = stats.get('processing', 0)
                pending = stats.get('pending', 0)
                
                progress = f"   Progress: {completed + failed}/{total} | "
                progress += f"✅ {completed} | ❌ {failed} | ⏳ {processing} | ⏸️  {pending}"
                print(f"\r{progress}", end='', flush=True)
                
                # Check if completed
                if status in ['completed', 'failed']:
                    print(f"\n\n🏁 Campaign {status}!")
                    print(f"\n📈 Final Stats:")
                    print(f"   Total Leads: {total}")
                    print(f"   Completed: {completed}")
                    print(f"   Failed: {failed}")
                    print(f"   Voice Calls: {stats.get('voice_calls', 0) if 'voice_calls' in stats else 'N/A'}")
                    break
                
                time.sleep(2)
                
            except Exception as e:
                print(f"\n❌ Error monitoring: {e}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Monitoring stopped by user")

def show_logs(campaign_id: int, limit: int = 20):
    """Show campaign logs."""
    print(f"\n📝 Recent logs for campaign {campaign_id}:\n")
    
    try:
        response = requests.get(f"{API_BASE_URL}/campaigns/{campaign_id}/logs?limit={limit}")
        response.raise_for_status()
        logs = response.json()
        
        if not logs:
            print("   No logs found")
            return
        
        for log in logs[:limit]:
            level = log.get('level', 'INFO')
            node = log.get('node_name', 'unknown')
            message = log.get('message', '')
            
            emoji = "ℹ️" if level == "INFO" else "❌"
            print(f"   {emoji} [{node}] {message}")
            
    except Exception as e:
        print(f"❌ Error fetching logs: {e}")

def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 Custom Voice Workflow Test")
    print("=" * 60)
    
    # Create campaign
    campaign_id = create_custom_voice_campaign(lead_count=3)
    if not campaign_id:
        sys.exit(1)
    
    # Start campaign
    if not start_campaign(campaign_id):
        sys.exit(1)
    
    # Monitor progress
    monitor_campaign(campaign_id)
    
    # Show logs
    show_logs(campaign_id)
    
    print("\n" + "=" * 60)
    print("✨ Test complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
