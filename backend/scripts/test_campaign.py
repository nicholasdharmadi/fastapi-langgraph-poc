#!/usr/bin/env python3
"""Test script for running a campaign."""
import sys
import time
import requests
from typing import Optional

API_BASE_URL = "http://localhost:8000/api"


def create_test_campaign(agent_type: str = "sms", lead_count: int = 10) -> Optional[int]:
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
    print("   (Press Ctrl+C to stop monitoring)\n")
    
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
                    print(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
                    print(f"   SMS Sent: {stats.get('sms_sent', 0)}")
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
    if len(sys.argv) < 2:
        print("Usage: python test_campaign.py <agent_type> [lead_count]")
        print("  agent_type: sms, voice, or both")
        print("  lead_count: number of leads (default: 10)")
        sys.exit(1)
    
    agent_type = sys.argv[1].lower()
    lead_count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    if agent_type not in ['sms', 'voice', 'both']:
        print("❌ Invalid agent_type. Must be: sms, voice, or both")
        sys.exit(1)
    
    print("=" * 60)
    print("🧪 FastAPI LangGraph POC - Campaign Test")
    print("=" * 60)
    
    # Create campaign
    campaign_id = create_test_campaign(agent_type, lead_count)
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
    print(f"   View campaign: http://localhost:5173/campaigns/{campaign_id}")
    print(f"   API docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()



