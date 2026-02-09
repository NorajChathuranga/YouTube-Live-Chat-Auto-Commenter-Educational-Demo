import time
import os
import threading
import msvcrt
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ===== SETTINGS =====
DELAY_SECONDS = 5  # default delay between each message
# ====================

# ---- EMOJI LIST ----
EMOJIS = {
    "1": ("❤️", "Red Heart"),
    "2": ("🔥", "Fire"),
    "3": ("😂", "Laughing"),
    "4": ("👍", "Thumbs Up"),
    "5": ("🎉", "Party"),
    "6": ("💯", "100"),
    "7": ("😍", "Heart Eyes"),
    "8": ("🙏", "Pray"),
    "9": ("💪", "Strong"),
    "10": ("⭐", "Star"),
    "11": ("🎶", "Music"),
    "12": ("👏", "Clap"),
    "13": ("😎", "Cool"),
    "14": ("🤩", "Starstruck"),
    "15": ("💜", "Purple Heart"),
    "16": ("💙", "Blue Heart"),
    "17": ("🫶", "Heart Hands"),
    "18": ("✨", "Sparkles"),
    "19": ("🥰", "Love"),
    "20": ("🤗", "Hug"),
}

def show_emoji_menu():
    """Display emoji menu."""
    print("  ┌──────────────────────────────────┐")
    print("  │        📋 EMOJI PICKER           │")
    print("  ├──────────────────────────────────┤")
    for num, (emoji, name) in EMOJIS.items():
        print(f"  │  [{num:>2}] {emoji}  {name:<20}│")
    print("  └──────────────────────────────────┘")

def input_with_emojis(prompt):
    """Ask for message with emoji support."""
    print(prompt)
    show_emoji_menu()
    print("  💡 Type your message. To add emoji, use {number}")
    print("     Example: Hello {1}{2} World → Hello ❤️🔥 World")
    print("-"*50)
    raw = input("  ➤ ").strip()
    # Replace {number} with actual emojis
    for num, (emoji, _) in EMOJIS.items():
        raw = raw.replace(f"{{{num}}}", emoji)
    return raw

# ---- USE A SEPARATE PROFILE (no need to close Chrome!) ----
PROFILE_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "Selenium_UC_Profile")

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")

# ---- START UNDETECTED CHROME (Google login works!) ----
print("="*50)
print("  🎬 YouTube Live Chat Auto-Commenter")
print("="*50)
print("Starting Chrome (undetected)...")
try:
    driver = uc.Chrome(options=options, user_data_dir=PROFILE_DIR, version_main=144)
except Exception as e:
    print(f"ERROR starting Chrome: {e}")
    print("Tip: Make sure no other Selenium Chrome is running. Try again.")
    exit(1)

time.sleep(3)  # let Chrome fully start
wait = WebDriverWait(driver, 60)

# ---- CHECK IF LOGGED IN ----
try:
    driver.get("https://www.youtube.com")
except Exception:
    print("ERROR: Chrome disconnected. Try running the script again.")
    exit(1)
time.sleep(5)

# Check if user is logged in by looking for avatar button
try:
    driver.find_element(By.CSS_SELECTOR, "button#avatar-btn, img.yt-spec-avatar-shape__avatar")
    print("✅ You are logged in to YouTube!")
except Exception:
    print("⚠️  You are NOT logged in. Please log in to YouTube now.")
    print("   Log in manually in the Chrome window, then press ENTER here to continue...")
    input()

# ---- OPEN LIVE STREAM ----
print("-"*50)
LIVE_STREAM_URL = input("🔗 Enter YouTube Live Stream URL: ").strip()
if not LIVE_STREAM_URL:
    print("No URL entered. Exiting.")
    driver.quit()
    exit(1)
print(f"Opening live stream: {LIVE_STREAM_URL}")
driver.get(LIVE_STREAM_URL)
print("Page opened. Waiting for it to load...")
time.sleep(10)  # let the page fully load

# ---- TRY TO FIND CHAT (iframe or direct) ----
print("Looking for live chat...")

try:
    # Method 1: Try iframe-based chat
    iframe = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "iframe#chatframe, iframe[src*='live_chat']")
        )
    )
    driver.switch_to.frame(iframe)
    print("Switched to chat iframe.")
except Exception:
    print("No chat iframe found. Trying to open chat popup...")
    try:
        # Method 2: Try clicking "Show chat replay" or chat button
        chat_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button#show-hide-button, ytd-toggle-button-renderer"
        )
        chat_btn.click()
        time.sleep(3)
        iframe = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe#chatframe, iframe[src*='live_chat']")
            )
        )
        driver.switch_to.frame(iframe)
        print("Switched to chat iframe after clicking button.")
    except Exception as e:
        print(f"ERROR: Could not find live chat. Is this a LIVE stream? Error: {e}")
        driver.quit()
        exit(1)

# ---- WAIT FOR CHAT INPUT ----
print("Waiting for chat input box...")
time.sleep(5)

CHAT_INPUT_SELECTORS = [
    "div#input[contenteditable='true']",
    "#input[contenteditable]",
    "yt-live-chat-text-input-field-renderer #input",
    "div[id='input'][role='textbox']",
    "#chat-input #input",
    "div[contenteditable='true']",
]

chat_input = None
for selector in CHAT_INPUT_SELECTORS:
    try:
        chat_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        print(f"Chat input found with: {selector}")
        break
    except Exception:
        continue

if not chat_input:
    print("ERROR: Chat input not found. Make sure:")
    print("  1. This is an ACTIVE live stream (not ended)")
    print("  2. You are logged in to YouTube")
    print("  3. Chat is not disabled by the streamer")
    driver.quit()
    exit(1)

# ---- ASK FOR CUSTOM MESSAGE ----
print("-"*50)
message = input_with_emojis("📝 Enter your message to auto-send:")
if not message:
    print("No message entered. Exiting.")
    driver.quit()
    exit(1)

delay = input(f"⏱️  Delay between messages in seconds (default {DELAY_SECONDS}): ").strip()
if delay.isdigit():
    DELAY_SECONDS = int(delay)

print("\n" + "="*50)
print("  ✅ READY! Here are your controls:")
print("="*50)
print("  [P] Pause  → Change message / delay / YouTube link")
print("  [Ctrl+C]   → Stop and quit")
print("-"*50)
print(f"  📝 Message : {message}")
print(f"  ⏱️  Delay   : {DELAY_SECONDS}s")
print(f"  🔗 Stream  : {LIVE_STREAM_URL}")
print("="*50 + "\n")

# ---- FUNCTION TO SWITCH TO NEW STREAM ----
def switch_stream(new_url):
    """Navigate to a new live stream and re-find the chat input."""
    global LIVE_STREAM_URL, chat_input, iframe
    LIVE_STREAM_URL = new_url
    driver.switch_to.default_content()
    driver.get(LIVE_STREAM_URL)
    print("Page opened. Waiting for it to load...")
    time.sleep(10)

    print("Looking for live chat...")
    try:
        iframe = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "iframe#chatframe, iframe[src*='live_chat']")
            )
        )
        driver.switch_to.frame(iframe)
        print("Switched to chat iframe.")
    except Exception as e:
        print(f"ERROR: Could not find live chat on new stream: {e}")
        return False

    time.sleep(5)
    chat_input = None
    for selector in CHAT_INPUT_SELECTORS:
        try:
            chat_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print(f"Chat input found with: {selector}")
            break
        except Exception:
            continue

    if not chat_input:
        print("ERROR: Chat input not found on new stream.")
        return False
    return True

# ---- SEND MESSAGES WITH PAUSE/RESUME ----
paused = False

def check_keyboard():
    """Listen for 'P' key to pause/resume."""
    global paused, message, DELAY_SECONDS
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode("utf-8", errors="ignore").lower()
            if key == "p":
                paused = True
                print("\n⏸️  PAUSED!")
                print("="*50)
                print("  Options:")
                print("  [1] Change message")
                print("  [2] Change delay")
                print("  [3] Change YouTube link")
                print("  [4] Show current settings")
                print("  [5] Resume")
                print("  [6] Quit")
                print("="*50)
                choice = input("  Choose (1-6): ").strip()

                if choice == "1":
                    new_msg = input_with_emojis("📝 Enter new message:")
                    if new_msg:
                        message = new_msg
                        print(f"✅ Message changed to: '{message}'")
                elif choice == "2":
                    new_delay = input(f"⏱️  Enter new delay in seconds (current: {DELAY_SECONDS}): ").strip()
                    if new_delay.isdigit():
                        DELAY_SECONDS = int(new_delay)
                        print(f"✅ Delay changed to: {DELAY_SECONDS}s")
                elif choice == "3":
                    new_url = input("🔗 Enter new YouTube live stream URL: ").strip()
                    if new_url:
                        print(f"Switching to: {new_url}")
                        if switch_stream(new_url):
                            print(f"✅ Stream changed to: {LIVE_STREAM_URL}")
                        else:
                            print("⚠️  Failed to switch. Resuming on old stream.")
                elif choice == "4":
                    print("="*50)
                    print(f"  📝 Message : {message}")
                    print(f"  ⏱️  Delay   : {DELAY_SECONDS}s")
                    print(f"  🔗 Stream  : {LIVE_STREAM_URL}")
                    print("="*50)
                    input("  Press ENTER to go back...")
                    paused = True
                    print("\n⏸️  Still paused. Choose again:")
                    return  # will re-trigger on next P press
                elif choice == "6":
                    print("Quitting...")
                    os._exit(0)

                print("▶️  RESUMED!")
                print("="*50)
                paused = False
        time.sleep(0.1)

# Start keyboard listener in background
kb_thread = threading.Thread(target=check_keyboard, daemon=True)
kb_thread.start()

print("🚀 Auto-commenting started!\n")

count = 0
try:
    while True:
        if paused:
            time.sleep(0.5)
            continue
        try:
            chat_input.click()
            time.sleep(0.5)
            chat_input.send_keys(message)
            time.sleep(0.5)
            chat_input.send_keys(Keys.ENTER)
            count += 1
            print(f"✉️  Message {count} sent: '{message}'")
        except Exception as e:
            print(f"Send failed (retrying next cycle): {e}")
        time.sleep(DELAY_SECONDS)
except KeyboardInterrupt:
    print(f"\nStopped after {count} messages.")
finally:
    driver.quit()
