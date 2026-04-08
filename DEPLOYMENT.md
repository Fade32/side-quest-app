# Side Quest App - Deployment Guide

## ✅ Data Cleared
All user data has been reset. The app is ready for deployment!

---

## 🚀 Deployment Options (Cheapest to Most Expensive)

### 1. **FREE - Render.com (Recommended for Beginners)** 💰 FREE

**What you get:**
- Free tier: 750 hours/month
- Auto-sleeps after 15 min of inactivity (wakes up in ~30 seconds)
- Perfect for testing and small groups

**Steps:**
1. Create account at [render.com](https://render.com)
2. Push your code to GitHub
3. Create a new "Web Service"
4. Connect your GitHub repo
5. Configure:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && python app.py`
   - **Environment:** Python 3
6. Deploy!

**Pros:** 
- Completely free
- Easy setup
- Automatic HTTPS
- Git integration

**Cons:**
- Sleeps after 15 min (first request takes ~30s to wake)
- Limited to 750 hours/month

---

### 2. **FREE - PythonAnywhere** 💰 FREE

**What you get:**
- Always-on (doesn't sleep)
- 512MB storage
- Limited to 100k hits/day

**Steps:**
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your code via Git or file upload
3. Set up a web app:
   - Framework: Flask
   - Python version: 3.10+
4. Configure WSGI file to point to your app.py
5. Reload web app

**Pros:**
- Always on (no sleep)
- Free forever
- Simple interface

**Cons:**
- Limited resources
- Manual deployment
- Slower than paid options

---

### 3. **FREE - Railway** 💰 $5 credit/month (effectively free for small apps)

**What you get:**
- $5 free credit monthly
- Your app will likely use $0-3/month
- No sleep time
- Fast performance

**Steps:**
1. Sign up at [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Select your repo
4. Railway auto-detects Python
5. Add environment variables if needed
6. Deploy!

**Pros:**
- No sleep
- Fast
- Great developer experience
- Usually stays under $5/month

**Cons:**
- Requires credit card (even for free tier)
- Can exceed $5 with heavy usage

---

### 4. **FREE - Fly.io** 💰 FREE (with resource limits)

**What you get:**
- 3 shared-cpu VMs
- 256MB RAM per VM
- 160GB bandwidth/month

**Steps:**
1. Install flyctl: `iwr https://fly.io/install.ps1 -useb | iex`
2. Sign up: `flyctl auth signup`
3. In your project folder: `flyctl launch`
4. Follow prompts (select region, etc.)
5. `flyctl deploy`

**Pros:**
- No sleep
- Good performance
- Multiple regions

**Cons:**
- More technical setup
- Requires flyctl CLI

---

### 5. **PAID - DigitalOcean App Platform** 💰 $5/month

**What you get:**
- Always on
- 512MB RAM
- Good performance
- Easy scaling

**Steps:**
1. Sign up at [digitalocean.com](https://www.digitalocean.com)
2. Create "App"
3. Connect GitHub repo
4. Configure build settings
5. Deploy

**Pros:**
- Reliable
- Good support
- Easy to scale
- Predictable pricing

**Cons:**
- Costs $5/month
- Overkill for small groups

---

## 📝 Recommended Setup for Your App

### For Testing/Personal Use:
→ **Render.com (FREE)** - Perfect for trying it out

### For Small Groups (5-20 people):
→ **Railway** or **Render.com** - No sleep issues, good performance

### For Larger Groups (50+ people):
→ **DigitalOcean ($5/month)** or **Railway** - Reliable and fast

---

## 🛠️ Pre-Deployment Checklist

Before deploying, update these files:

### 1. **requirements.txt** (already exists)
```txt
Flask==3.0.0
flask-cors==4.0.0
```

### 2. **Update script.js** - Change API URL
Replace this line in `frontend/script.js`:
```javascript
const API_URL = 'http://localhost:5000/api';
```
With your deployment URL:
```javascript
const API_URL = 'https://your-app-name.onrender.com/api';
// or wherever you deploy
```

### 3. **Optional: Add Procfile** (for some platforms)
Create `Procfile` in the root:
```
web: cd backend && python app.py
```

### 4. **Optional: Add runtime.txt** (specify Python version)
Create `runtime.txt`:
```
python-3.14.4
```

---

## 🚀 Quick Start - Render.com Deployment

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to render.com
   - New → Web Service
   - Connect GitHub repo
   - Name: `side-quest-app`
   - Build: `cd backend && pip install -r requirements.txt`
   - Start: `cd backend && python app.py`
   - Click "Create Web Service"

3. **Update API URL:**
   - Wait for deployment
   - Copy your Render URL (e.g., `https://side-quest-app.onrender.com`)
   - Update `frontend/script.js` line 1:
     ```javascript
     const API_URL = 'https://side-quest-app.onrender.com/api';
     ```
   - Commit and push again

4. **Done!** 🎉
   Visit `https://side-quest-app.onrender.com`

---

## 💡 Tips

- **Data Persistence:** Your `data.json` file will persist on most platforms, but consider using a real database (PostgreSQL, MongoDB) for production
- **Environment Variables:** Store sensitive data in environment variables, not in code
- **Custom Domain:** Most platforms allow custom domains (yourapp.com) for free or cheap
- **HTTPS:** All recommended platforms provide free HTTPS
- **Monitoring:** Use platform's built-in logs to debug issues

---

## 🆘 Troubleshooting

**App won't start:**
- Check logs on your platform's dashboard
- Verify Python version matches
- Ensure all dependencies in requirements.txt

**CORS errors:**
- Update CORS settings in app.py if needed
- Check API_URL in frontend matches deployment URL

**Data not saving:**
- Check file permissions
- Consider using environment-specific data storage

---

## 📞 Need Help?

Most platforms have:
- Documentation
- Community forums
- Discord servers
- Free support

**Recommended:** Start with Render.com - it's the easiest and completely free!
