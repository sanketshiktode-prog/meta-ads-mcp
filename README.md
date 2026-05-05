# Meta Ads MCP Server

A Model Context Protocol server that lets Claude create and manage Meta Ads campaigns automatically.

## What This Does

Claude can now:
- ✅ Create campaigns following your 5 SOPs
- ✅ List all your campaigns
- ✅ Get campaign details
- ✅ Check connection to Meta

All integrated as native tools in Claude.

## Your 5 SOPs (Built-in)

1. Manual campaign setup (not Advantage+)
2. Audience Network disabled
3. Advantage+ Audience disabled
4. Location & Age targeting restricted
5. All Ad Enhancements disabled

## Files

- `server.py` - Main MCP server
- `requirements.txt` - Python dependencies
- `Procfile` - Render deployment config
- `runtime.txt` - Python version
- `DEPLOY_GUIDE.md` - Step-by-step deployment

## Quick Deploy

1. Push files to GitHub
2. Deploy on Render.com
3. Set environment variables
4. Done!

See `DEPLOY_GUIDE.md` for detailed steps.

## Tools Available to Claude

- `test_meta_connection` - Test Meta API connection
- `get_sop_checklist` - View the 5 SOPs
- `create_campaign` - Create new campaign
- `list_campaigns` - List all campaigns
- `get_campaign_details` - Get campaign info

---

**Ready?** Follow `DEPLOY_GUIDE.md`
