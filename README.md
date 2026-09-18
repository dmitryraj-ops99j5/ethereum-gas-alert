ethereum-gas-alert

I got tired of manually checking Etherscan or overpaying for gas when doing standard transactions. This is a minimal background runner that polls the Ethereum network (via Cloudflare's public RPC or Etherscan API) and sends a Telegram ping and a system beep when the gas price drops below your target.

It keeps a small state file on disk to prevent spamming notifications once the threshold is crossed.

Installation:

pip install -r requirements.txt

Usage:

Configure your Telegram bot token and chat ID in your environment variables, or pass them directly as flags.

Set env vars:
set TELEGRAM_BOT_TOKEN=123456:ABC-DEF
set TELEGRAM_CHAT_ID=987654321

Run the monitor to alert when gas drops below 25 Gwei:
python gas_alert.py --threshold 25 --interval 60

By default it uses the public Cloudflare RPC, so you do not even need an Infura or Etherscan API key to get started.

Options:
python gas_alert.py --help

<!-- verified: 2026-09-18 -->
