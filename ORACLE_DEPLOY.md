# Oracle Cloud VPS — Deploy Guide

## Step 1 — Create account

1. Go to **cloud.oracle.com** → click **Start for free**
2. Fill in: name, email, home region (choose one close to you — e.g. `sa-saopaulo-1`)
3. Credit card required for identity verification — **no charge is made**
4. Complete email verification and wait for account activation (usually instant, sometimes up to 5 min)

---

## Step 2 — Create the VM

1. Log into the OCI console → top-left menu → **Compute → Instances → Create instance**

2. **Name:** `jansen-dev-agent`

3. **Image and shape** — click **Edit**:
   - Image: **Ubuntu 22.04** (Canonical)
   - Shape: click **Change shape** → **Ampere** tab → `VM.Standard.A1.Flex`
   - OCPU: `1` · Memory: `6 GB`
   - Confirm it shows **Always Free-eligible** ✓

   > ⚠️ If you get "Out of host capacity" — this is common on ARM. Two options:
   > - Try a different region (US East or US West tend to have more capacity)
   > - Use **VM.Standard.E2.1.Micro** (AMD, 1GB RAM) instead — also Always Free, slightly less RAM but works fine for this project

4. **SSH keys** — click **Generate a key pair for me** → **Save private key**
   - File saves as `ssh-key-YYYY-MM-DD.key` in your Downloads

5. Leave everything else as default → **Create**

6. Wait ~2 minutes for the instance to reach **RUNNING** state

7. Copy the **Public IP address** from the instance details page

---

## Step 3 — Connect via SSH

On your Mac terminal:

```bash
chmod 400 ~/Downloads/ssh-key-*.key

ssh -i ~/Downloads/ssh-key-*.key ubuntu@<PUBLIC_IP>
```

Type `yes` when asked about host authenticity. You should see the Ubuntu welcome prompt.

---

## Step 4 — Run the deploy script

Inside the VM, paste this single command:

```bash
curl -sL https://raw.githubusercontent.com/ToniJansen/jansen-dev-agent/main/deploy.sh | bash
```

The script will:
- Install Python 3, pip, and git
- Clone the repo
- Install all Python dependencies
- Pause and ask you to fill in `.env`

---

## Step 5 — Fill in `.env`

When the script pauses, open the file:

```bash
nano ~/jansen-dev-agent/jansen_dev_agent/.env
```

Fill in the values:

```
GROQ_API_KEY=gsk_jQ7t68...
GROQ_MODEL=llama-3.3-70b-versatile
TELEGRAM_BOT_TOKEN=8731037127:AAG9...
TELEGRAM_CHAT_ID=6492284230
GITHUB_TOKEN=gho_W6i7...
GITHUB_REPO=ToniJansen/jansen-dev-agent
CODE_TARGET_FILE=../demo/order_manager.py
MEETINGS_DIR=../demo/meetings
```

Save: `Ctrl+O` → Enter → `Ctrl+X`

Then press **Enter** in the terminal to continue the deploy script.

---

## Step 6 — Verify

```bash
# Bot is running and will auto-restart on crash
sudo systemctl status jansen-bot

# Watch live logs
sudo journalctl -u jansen-bot -f

# Check cron jobs were registered
crontab -l
```

Expected output from `systemctl status`:
```
● jansen-bot.service - Jansen Dev Agent — Telegram Bot
     Loaded: loaded (/etc/systemd/system/jansen-bot.service; enabled)
     Active: active (running)
```

Send `/start` to `@jansen_dev_agent_bot` in Telegram to confirm it's live.

---

## Step 7 — Stop bot on your Mac

Since the bot must run on only one machine (Telegram long-polling limitation):

```bash
# On your Mac — stop the local bot process
pkill -f "bot_listener.py"
```

The scheduled agents (`overnight_agent.py` and `morning_agent.py`) can stay running on the Mac if you want — duplicate Telegram messages from both machines are harmless.

---

## Useful commands (on the VPS)

```bash
# Restart bot after a code update
git -C ~/jansen-dev-agent pull && sudo systemctl restart jansen-bot

# View overnight agent log
tail -f /tmp/jansen_overnight.log

# View morning agent log
tail -f /tmp/jansen_morning.log

# Manually trigger overnight review
cd ~/jansen-dev-agent/jansen_dev_agent && python3 overnight_agent.py

# Manually trigger morning agent
cd ~/jansen-dev-agent/jansen_dev_agent && python3 morning_agent.py
```

---

## Update workflow

Whenever you push changes to GitHub:

```bash
# On the VPS
git -C ~/jansen-dev-agent pull && sudo systemctl restart jansen-bot
```
