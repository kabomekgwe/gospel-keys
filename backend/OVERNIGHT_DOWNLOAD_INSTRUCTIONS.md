# 🌙 Overnight Download Instructions for Llama 3.3 70B

## Quick Start

Run this ONE command from the `backend` directory:

```bash
./download_overnight.sh
```

That's it! Your Mac will stay awake and download the model overnight.

---

## What Happens

1. **Your Mac Won't Sleep** - Uses macOS `caffeinate` command
2. **Downloads 37GB** - Llama 3.3 70B 4-bit quantized model
3. **Shows Progress** - Real-time updates in terminal
4. **Logs Everything** - Saves to `download_log.txt`
5. **Plays Sound** - Notification when complete
6. **Stays Cached** - Never downloads again (saved in `~/.cache/huggingface/`)

---

## Step-by-Step Instructions

### 1. Navigate to Backend Directory

```bash
cd /Users/kabo/Desktop/projects/youtube-transcript/backend
```

### 2. Activate Python Environment

```bash
source .venv/bin/activate
```

### 3. Run the Download Script

```bash
./download_overnight.sh
```

### 4. (Optional) Close Terminal Window

You can minimize or close the terminal window - the download will continue!

**Important:** Keep Terminal.app running (don't quit the application)

---

## Alternative: Run in Background

If you want to run in background and see output later:

```bash
# Run in background and save output
nohup ./download_overnight.sh > download_output.log 2>&1 &

# Check progress
tail -f download_log.txt

# Or check full output
tail -f download_output.log
```

---

## What Gets Downloaded

- **Model**: `mlx-community/Llama-3.3-70B-Instruct-4bit`
- **Size**: 37GB
- **Location**: `~/.cache/huggingface/hub/models--mlx-community--Llama-3.3-70B-Instruct-4bit/`
- **Time**: 15-30 minutes (depending on internet speed)

---

## Progress Monitoring

### Check Download Status

```bash
# Watch the log in real-time
tail -f download_log.txt
```

### Check Disk Space

```bash
# Check free space
df -h ~

# Watch download size grow
du -sh ~/.cache/huggingface/hub/models--mlx-community--Llama-3.3-70B-Instruct-4bit/
```

### Check Network Activity

Open **Activity Monitor** (Applications → Utilities → Activity Monitor):
- Click **Network** tab
- Look for Python process with high download rate

---

## Preventing Sleep (How It Works)

The script uses macOS `caffeinate` command:

```bash
caffeinate -dim python download_llama_overnight.py
```

**Flags:**
- `-d` - Prevents display from sleeping
- `-i` - Prevents system idle sleep
- `-m` - Prevents disk idle sleep

**Note:** You can manually turn off the display with **Ctrl+Shift+Eject** (or Ctrl+Shift+Power on newer Macs) - the download will continue!

---

## Troubleshooting

### If Download Fails

**Error: "Multi-model service not available"**

```bash
# Install MLX
pip install mlx>=0.30.0 mlx-lm>=0.28.4

# Try again
./download_overnight.sh
```

**Error: "Permission denied"**

```bash
# Make script executable
chmod +x download_overnight.sh

# Try again
./download_overnight.sh
```

**Error: "No space left on device"**

```bash
# Check free space (need 40GB+)
df -h ~

# Clean up if needed
# Delete old Hugging Face cache (if safe):
# rm -rf ~/.cache/huggingface/hub/models--mlx-community--Qwen*
```

---

### If Mac Still Sleeps

**Manual Prevention:**

```bash
# Run this in a separate terminal
caffeinate -dis

# Keep that terminal open
# Ctrl+C to stop when download finishes
```

**System Preferences:**

1. Go to **System Settings** → **Displays**
2. Set "Turn display off after" to **Never**
3. Go to **Battery** (or **Energy Saver**)
4. Set "Prevent automatic sleeping when display is off" to **checked**

(Remember to change back after download!)

---

### If Download Is Slow

**Check Internet Speed:**

```bash
# Test download speed
curl -o /dev/null http://speedtest.wdc01.softlayer.com/downloads/test100.zip

# You should see > 10 MB/s for fast download
```

**Expected Times:**
- 100 Mbps: ~50 minutes
- 500 Mbps: ~10 minutes
- 1 Gbps: ~5 minutes

---

## After Download Completes

### Verify Installation

```bash
cd backend
source .venv/bin/activate

python -c "
from app.services.multi_model_service import multi_model_service
info = multi_model_service.get_model_info()
print('✅ Llama 3.3 70B ready!' if 'Llama-3.3-70B' in str(info) else '❌ Not found')
"
```

### Test Generation

```bash
python -c "
from app.services.multi_model_service import multi_model_service

response = multi_model_service.generate(
    prompt='Explain a ii-V-I progression in 2 sentences',
    complexity=5,
    max_tokens=100
)
print(response)
"
```

### Run Your Backend

```bash
# Start FastAPI server
python -m uvicorn app.main:app --reload --port 8000

# Your app now uses Llama 3.3 70B for tutorials!
```

---

## Files Created

After running the script, you'll have:

1. **`download_log.txt`** - Detailed log of download process
2. **`download_overnight.sh`** - Shell script (already created)
3. **`download_llama_overnight.py`** - Python download script (already created)
4. **`~/.cache/huggingface/hub/models--mlx-community--Llama-3.3-70B-Instruct-4bit/`** - Downloaded model

---

## Disk Space Requirements

- **Before Download**: 40GB+ free space recommended
- **During Download**: 37GB (model files)
- **After Download**: 37GB permanently used (cached)

**To Free Space Later:**

```bash
# Only if you want to remove and re-download later
rm -rf ~/.cache/huggingface/hub/models--mlx-community--Llama-3.3-70B-Instruct-4bit/
```

---

## Security Notes

**Safe to Leave Running Overnight:**
- ✅ Script only downloads from official Hugging Face repository
- ✅ Uses secure HTTPS connections
- ✅ No external commands beyond MLX library
- ✅ Logs all activity to `download_log.txt`

**Network Security:**
- Download comes from `huggingface.co` (trusted source)
- No personal data sent anywhere
- No external services accessed

---

## FAQ

**Q: Can I use my Mac while downloading?**
A: Yes! You can browse, work, etc. Just keep Terminal.app running.

**Q: What if I close the laptop lid?**
A: The caffeinate command prevents sleep even with lid closed (on some Macs). To be safe, leave it open or connected to power with display on.

**Q: Can I pause and resume?**
A: Hugging Face downloads support resuming. If interrupted, run the script again.

**Q: Will this drain my battery?**
A: Yes - keep your Mac plugged in during download!

**Q: How do I know it's working?**
A: Check `download_log.txt` with `tail -f download_log.txt`

**Q: Can I download during the day instead?**
A: Absolutely! Just run `./download_overnight.sh` anytime.

---

## Summary

**To download Llama 3.3 70B overnight:**

1. `cd backend`
2. `source .venv/bin/activate`
3. `./download_overnight.sh`
4. Go to sleep! 😴

**Next morning:**
- Check `download_log.txt` for "🎉 DOWNLOAD COMPLETE!"
- Your app now has GPT-4 quality AI running locally!

---

**Questions?** Check the logs or run the script again - it's safe to re-run.
