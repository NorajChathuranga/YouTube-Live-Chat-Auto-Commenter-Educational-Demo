# YouTube Live Chat Auto-Commenter (Educational Demo)

This repository contains a single script, [youtube_chat_demo.py](youtube_chat_demo.py), which automates a Chrome browser to open a YouTube Live stream, locate the live chat input, and post a message on an interval.

## Responsible use

- Use this only for **education/testing**, and preferably on **your own stream** or with **explicit permission**.
- Avoid spam. Automated posting may violate YouTube rules and can lead to account limitations.
- For production/approved automation, prefer the official **YouTube Data API**.

## Features

- Prompts at startup for:
	- Live stream URL
	- Message text (with an emoji picker)
	- Delay between messages (seconds)
- Tries multiple selectors to find the chat input inside the live chat iframe.
- Runtime controls:
	- Press **P** to pause and open a menu:
		- Change message
		- Change delay
		- Change YouTube link (switch stream)
		- Show current settings
		- Quit
	- Press **Ctrl+C** to stop

## Requirements

- Windows (uses `msvcrt` for key detection)
- Python 3.10+
- Google Chrome installed

Python packages used:

- `selenium`
- `undetected-chromedriver`

## Install

```bash
python -m pip install selenium undetected-chromedriver
```

## Run

```bash
python youtube_chat_demo.py
```

What you’ll see:

1. The script opens YouTube and checks whether you are logged in.
2. It asks for the YouTube live stream URL.
3. It asks for the message and delay.
4. It starts posting the message repeatedly.

## Emoji input

When prompted for a message, you can insert emojis using the `{number}` syntax shown in the emoji menu.

Example:

- Input: `Hello {1}{2}`
- Sends: `Hello ❤️🔥`

## Profile / login

The script uses a dedicated Chrome profile directory under:

`%LOCALAPPDATA%\Google\Chrome\Selenium_UC_Profile`

Your login state is stored there.

## Troubleshooting

### ChromeDriver / Chrome version mismatch

If you see an error like “ChromeDriver only supports Chrome version …”, update the line in [youtube_chat_demo.py](youtube_chat_demo.py) that looks like:

```py
version_main=144
```

Set it to your installed Chrome **major version**.

### Chat input not found

Common causes:

- The stream is not currently live (ended / replay)
- Live chat is disabled by the streamer
- You don’t have permission to chat (subscriber-only, slow mode, age restrictions, etc.)

### Chrome opens then closes / disconnected

- Close any other Selenium-driven Chrome instances and run again.
- Try running only one copy of the script at a time.
