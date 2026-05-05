"""
Meta Ads MCP Server - Full Campaign Management
Comprehensive tool for creating complete Meta Ads campaigns with ad sets, targeting, and forms
"""

import os
import requests
import json
from typing import Any, List, Dict
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

# Location to geo targeting code mapping
LOCATION_MAPPING = {
    "dubai": 2420866,
    "sharjah": 2420869,
    "abu dhabi": 2420868,
    "abudhabi": 2420868,
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
        return {
            "status": "❌ Error",
            "error": str(e)
        }


def get_campaign_creatives(campaign_id: str) -> Dict:
    """Fetch creatives and ads from an existing campaign"""
    try:
        headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
        url = f"{BASE_URL}/{campaign_id}/adsets"
        params = {
            "fields": "id,name,creative_sequence",
            "limit": 100
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            ad_sets = response.json().get("data", [])
            
            creatives = []
            ads_data = []
            
            for ad_set in ad_sets:
                # Get ads in this ad set
                ads_url = f"{BASE_URL}/{ad_set['id']}/ads"
                ads_params = {
                    "fields": "id,name,creative,adset_id,adlabels",
                    "limit": 100
                }
                ads_response = requests.get(ads_url, headers=headers, params=ads_params)
                
                if ads_response.status_code == 200:
                    ads = ads_response.json().get("data", [])
                    for ad in ads:
                        creative_id = ad.get("creative", {}).get("id") if isinstance(ad.get("creative"), dict) else ad.get("creative")
                        creatives.append(creative_id)
                        ads_data.append({
                            "ad_id": ad.get("id"),
                            "ad_name": ad.get("name"),
                            "creative_id": creative_id,
                            "adset_id": ad_set["id"]
                        })
            
            return {
                "status": "✅ Fetched",
                "count": len(ads_data),
                "creatives": list(set(creatives)),  # Unique creatives
                "ads": ads_data
            }
        else:
            return {
                "status": "❌ Failed",
                "error": response.json().get("error", {}).get("message")
            }
    except Exception as e:
        return {"status": "❌ Error", "error": str(e)}


def create_full_campaign(campaign_name: str, ad_sets_config: List[Dict], form_name: str, ref_campaign_id: str) -> Dict:
    """
    Create a complete campaign with multiple ad sets and targeting
    
    Args:
        campaign_name: Name of the new campaign
        ad_sets_config: List of ad set configurations
        form_name: Lead generation form name
        ref_campaign_id: Reference campaign to copy creatives from
    """
    try:
        headers = {"Authorization": f"Bearer {META_ACCESS_TOKEN}"}
        
        # Step 1: Create main campaign
        campaign_url = f"{BASE_URL}/{ACCOUNT_ID}/campaigns"
        campaign_payload = {
            "name": campaign_name,
            "objective": "LEAD_GENERATION",
            "special_ad_categories": ["REAL_ESTATE"],
            "status": "PAUSED"
        }
        
        campaign_response = requests.post(campaign_url, json=campaign_payload, headers=headers)
        
        if campaign_response.status_code != 201:
            error_msg = campaign_response.json().get("error", {}).get("message")
            return {
                "status": "❌ Campaign Creation Failed",
                "error": error_msg
            }
        
        campaign_id = campaign_response.json().get("id")
        
        # Step 2: Fetch creatives from reference campaign
        ref_creatives = get_campaign_creatives(ref_campaign_id)
        creatives_available = ref_creatives.get("creatives", [])
        
        # Step 3: Create ad sets with targeting
        created_adsets = []
        
        for adset_config in ad_sets_config:
            adset_name = adset_config.get("name", "Ad Set")
            location = adset_config.get("location", "Dubai").lower()
            age_min = adset_config.get("age_min", 30)
            age_max = adset_config.get("age_max", 40)
            budget_daily = adset_config.get("budget_daily", 2500)
            
            # Get location geo code
            geo_location_id = LOCATION_MAPPING.get(location, 2420866)
            
            adset_url = f"{BASE_URL}/{ACCOUNT_ID}/adsets"
            adset_payload = {
                "name": adset_name,
                "campaign_id": campaign_id,
                "daily_budget": int(budget_daily * 100),  # Convert to cents
                "billing_event": "IMPRESSIONS",
                "optimization_goal": "LEAD_GENERATION",
                "targeting": {
                    "geo_locations": {
                        "regions": [
                            {
                                "key": str(geo_location_id)
                            }
                        ]
                    },
                    "age_min": age_min,
                    "age_max": age_max
                },
                "status": "PAUSED"
            }
            
            adset_response = requests.post(adset_url, json=adset_payload, headers=headers)
            
            if adset_response.status_code == 201:
                adset_id = adset_response.json().get("id")
                created_adsets.append({
                    "✅ Status": "Created",
                    "adset_name": adset_name,
                    "adset_id": adset_id,
                    "location": location.title(),
                    "age_group": f"{age_min}-{age_max}",
                    "budget_daily_inr": budget_daily
                })
            else:
                error_msg = adset_response.json().get("error", {}).get("message", "Unknown error")
                created_adsets.append({
                    "❌ Status": "Failed",
                    "adset_name": adset_name,
                    "error": error_msg
                })
        
        successful_adsets = [a for a in created_adsets if "adset_id" in a]
        
        return {
            "✅ Status": "Campaign Created Successfully",
            "Campaign ID": campaign_id,
            "Campaign Name": campaign_name,
            "Form Name": form_name,
            "Ad Sets Created": len(successful_adsets),
            "Total Ad Sets": len(created_adsets),
            "Ad Sets": created_adsets,
            "Reference Campaign ID": ref_campaign_id,
            "Creatives Available": len(creatives_available),
            "Message": "✅ Campaign structure created successfully!",
            "Next Steps": [
                "1. Go to Meta Ads Manager",
                "2. Open campaign: " + campaign_name,
                "3. For each ad set, attach creatives from reference campaign",
                "4. Link lead generation form: " + form_name,
                "5. Review all SOP compliance",
                "6. Activate campaign when ready"
            ],
            "SOP Compliance": SOP_RULES
        }
        
    except Exception as e:
        return {
            "status": "❌ Error",
            "error": str(e)
        }


def get_sop_checklist():
    """Return SOP checklist"""
    return {
        "status": "SOP Checklist for Real Estate Campaigns",
        "rules": SOP_RULES,
        "important": "All rules MUST be followed for lead quality"
    }


# Define tools for MCP
TOOLS = [
    {
        "name": "test_connection",
        "description": "Test connection to Meta Ads API",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_full_campaign",
        "description": "Create a complete lead generation campaign with multiple ad sets, targeting, and forms",
        "inputSchema": {
            "type": "object",
            "properties": {
                "campaign_name": {
                    "type": "string",
                    "description": "Campaign name (e.g., 'Azizi Venice by Claude')"
                },
                "ad_sets": {
                    "type": "array",
                    "description": "List of ad sets to create",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Ad set name (e.g., 'Dubai - 30-40')"
                            },
                            "location": {
                                "type": "string",
                                "description": "Location (Dubai, Sharjah, Abu Dhabi)"
                            },
                            "age_min": {
                                "type": "integer",
                                "description": "Minimum age"
                            },
                            "age_max": {
                                "type": "integer",
                                "description": "Maximum age"
                            },
                            "budget_daily": {
                                "type": "integer",
                                "description": "Daily budget in INR"
                            }
                        }
                    }
                },
                "form_name": {
                    "type": "string",
                    "description": "Lead generation form name"
                },
                "ref_campaign_id": {
                    "type": "string",
                    "description": "Reference campaign ID to copy creatives from"
                }
            },
            "required": ["campaign_name", "ad_sets", "form_name", "ref_campaign_id"]
        }
    },
    {
        "name": "get_sop_checklist",
        "description": "Get the 5 SOPs for real estate campaigns",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def handle_tool_call(tool_name: str, tool_input: dict) -> Any:
    """Route tool calls"""
    
    if tool_name == "test_connection":
        return test_connection()
    
    elif tool_name == "create_full_campaign":
        return create_full_campaign(
            campaign_name=tool_input.get("campaign_name"),
            ad_sets_config=tool_input.get("ad_sets", []),
            form_name=tool_input.get("form_name"),
            ref_campaign_id=tool_input.get("ref_campaign_id")
        )
    
    elif tool_name == "get_sop_checklist":
        return get_sop_checklist()
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


# Simple HTTP server for MCP
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
