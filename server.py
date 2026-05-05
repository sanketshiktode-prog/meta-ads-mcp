"""
Meta Ads MCP Server
Exposes Meta Ads operations as tools for Claude
"""

import os
import requests
import json
from typing import Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get credentials
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID")

if not META_ACCESS_TOKEN or not META_AD_ACCOUNT_ID:
    raise ValueError("Missing META_ACCESS_TOKEN or META_AD_ACCOUNT_ID in environment")

# Meta API base URL
BASE_URL = "https://graph.facebook.com/v18.0"
ACCOUNT_ID = META_AD_ACCOUNT_ID if META_AD_ACCOUNT_ID.startswith("act_") else f"act_{META_AD_ACCOUNT_ID}"

# SOP Requirements (your rules)
SOP_RULES = {
    "1": "Always use manual campaign setup (not Advantage+ or Tailored)",
    "2": "Disable Audience Network Placements",
    "3": "Disable Advantage+ Audience - further limit reach",
    "4": "Location & Age targeting must NOT be suggestions - manually set",
    "5": "Disable ALL Ad Enhancements"
}


def test_connection():
    """Test connection to Meta API"""
    try:
        url = f"{BASE_URL}/{ACCOUNT_ID}"
        headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "✅ Connected",
                "account_name": data.get("name"),
                "currency": data.get("currency"),
                "account_id": ACCOUNT_ID
            }
        else:
            return {
                "status": "❌ Connection Failed",
                "error": response.json().get("error", {}).get("message", "Unknown error")
            }
    except Exception as e:
        return {"status": "❌ Error", "error": str(e)}


def get_sop_checklist():
    """Return SOP checklist for campaign creation"""
    return {
        "status": "SOP Checklist for Real Estate Campaigns",
        "rules": SOP_RULES,
        "important": "All rules MUST be followed for lead quality. Campaigns are created in PAUSED state for review."
    }


def create_campaign(campaign_name: str, audience_description: str, budget_inr: int):
    """
    Create a new Meta Ads campaign following SOPs
    
    Args:
        campaign_name: Name of campaign (e.g., "Mumbai Real Estate - Q2")
        audience_description: Target audience (e.g., "Ages 25-55, Mumbai, interested in properties")
        budget_inr: Daily budget in INR
    
    Returns:
        Campaign creation result
    """
    
    try:
        headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
        url = f"{BASE_URL}/{ACCOUNT_ID}/campaigns"
        
        # Campaign payload following SOPs
        payload = {
            "name": campaign_name,
            "objective": "LEAD_GENERATION",
            "special_ad_categories": ["REAL_ESTATE"],
            "status": "PAUSED",  # Always PAUSED for review
            "daily_budget": budget_inr * 100  # Convert to cents
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            campaign_id = response.json().get("id")
            return {
                "status": "✅ Campaign Created",
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "state": "PAUSED - Review before launching",
                "budget_inr": budget_inr,
                "message": f"Campaign '{campaign_name}' created. Review in Meta Ads Manager, then activate.",
                "sop_reminder": "Ensure targeting follows all 5 SOPs before activation"
            }
        else:
            error = response.json().get("error", {})
            return {
                "status": "❌ Creation Failed",
                "error": error.get("message", "Unknown error"),
                "code": error.get("code")
            }
    
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e)
        }


def list_campaigns():
    """Get list of all campaigns in account"""
    try:
        headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
        url = f"{BASE_URL}/{ACCOUNT_ID}/campaigns"
        params = {
            "fields": "id,name,objective,status,created_time,daily_budget",
            "limit": 25
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            campaigns = response.json().get("data", [])
            return {
                "status": "✅ Retrieved",
                "count": len(campaigns),
                "campaigns": campaigns
            }
        else:
            return {
                "status": "❌ Failed",
                "error": response.json().get("error", {}).get("message")
            }
    
    except Exception as e:
        return {"status": "❌ Error", "error": str(e)}


def get_campaign_details(campaign_id: str):
    """Get detailed info about a specific campaign"""
    try:
        headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
        url = f"{BASE_URL}/{campaign_id}"
        params = {
            "fields": "id,name,objective,status,created_time,daily_budget,budget_remaining"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return {
                "status": "✅ Retrieved",
                "campaign": response.json()
            }
        else:
            return {
                "status": "❌ Failed",
                "error": response.json().get("error", {}).get("message")
            }
    
    except Exception as e:
        return {"status": "❌ Error", "error": str(e)}


# Define tools for MCP
TOOLS = [
    {
        "name": "test_meta_connection",
        "description": "Test connection to Meta Ads API account",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_sop_checklist",
        "description": "Get the 5 SOPs for real estate campaign creation",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_campaign",
        "description": "Create a new Meta Ads campaign for real estate lead generation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_name": {
                    "type": "string",
                    "description": "Campaign name (e.g., 'Mumbai Real Estate - May 2024')"
                },
                "audience_description": {
                    "type": "string",
                    "description": "Target audience details (e.g., 'Ages 25-55, Mumbai, interested in properties')"
                },
                "budget_inr": {
                    "type": "integer",
                    "description": "Daily budget in Indian Rupees"
                }
            },
            "required": ["campaign_name", "audience_description", "budget_inr"]
        }
    },
    {
        "name": "list_campaigns",
        "description": "Get list of all campaigns in the account",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_campaign_details",
        "description": "Get detailed information about a specific campaign",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "The campaign ID"
                }
            },
            "required": ["campaign_id"]
        }
    }
]


def handle_tool_call(tool_name: str, tool_input: dict) -> Any:
    """Route tool calls to appropriate functions"""
    
    if tool_name == "test_meta_connection":
        return test_connection()
    
    elif tool_name == "get_sop_checklist":
        return get_sop_checklist()
    
    elif tool_name == "create_campaign":
        return create_campaign(
            campaign_name=tool_input.get("campaign_name"),
            audience_description=tool_input.get("audience_description"),
            budget_inr=tool_input.get("budget_inr")
        )
    
    elif tool_name == "list_campaigns":
        return list_campaigns()
    
    elif tool_name == "get_campaign_details":
        return get_campaign_details(
            campaign_id=tool_input.get("campaign_id")
        )
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


# Simple HTTP server for MCP (compatible with Render)
if __name__ == "__main__":
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class MCPHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/health":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "healthy"}).encode())
            
            elif self.path == "/tools":
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"tools": TOOLS}).encode())
            
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                tool_name = data.get("tool_name")
                tool_input = data.get("input", {})
                
                result = handle_tool_call(tool_name, tool_input)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    port = int(os.getenv("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), MCPHandler)
    print(f"🚀 Meta Ads MCP Server running on port {port}")
    server.serve_forever()
