# Deploy to Render (5 minutes)

## What You Have
A Meta Ads MCP Server that Claude can use to create campaigns automatically.

## Step-by-Step Deploy

### Step 1: Push to GitHub (Free)

1. Create account on github.com (if you don't have)
2. Create new repository (name: `meta-ads-mcp`)
3. Upload all files from this folder to GitHub

**Via GitHub Web UI (easiest):**
- Go to github.com/new
- Name: `meta-ads-mcp`
- Click "Create repository"
- Click "uploading an existing file"
- Drag-drop all files here
- Commit

### Step 2: Deploy on Render (Free)

1. Go to **render.com**
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a Repository"**
4. Select your `meta-ads-mcp` repo
5. Fill in:
   - **Name**: `meta-ads-mcp`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`

6. Click **"Environment"** → Add these variables:
   ```
   META_ACCESS_TOKEN = [paste your token]
   META_AD_ACCOUNT_ID = [paste your account ID]
   ```

7. Click **"Deploy"**

⏳ Wait 2-3 minutes... Your server will be live!

### Step 3: Get Your Server URL

After deploy completes, you'll see a URL like:
```
https://meta-ads-mcp-abcd1234.onrender.com
```

**Test it:**
Open in browser:
```
https://meta-ads-mcp-abcd1234.onrender.com/health
```

Should show: `{"status": "healthy"}`

---

## Step 4: Connect Claude

Once your server is running, tell me:
- Your Render URL (e.g., `https://meta-ads-mcp-abcd1234.onrender.com`)

I'll configure Claude to connect to it.

---

## Troubleshooting

### Deploy fails with Python error
→ Make sure all files are uploaded to GitHub

### "health" endpoint returns error
→ Check that META_ACCESS_TOKEN and META_AD_ACCOUNT_ID are set correctly in Render

### "Connection failed" when using tools
→ Your Meta credentials are wrong. Regenerate them and update in Render

---

## What Next?

Once deployed:
1. ✅ Server running on Render (24/7)
2. ✅ Claude can access it
3. ✅ Create campaigns with: "Claude, create a campaign..."
4. ✅ Done!

Questions? Let me know!
