import argparse
import sys
import time
import winsound
import httpx

from gas_alert.notifiers import send_telegram_alert

# TODO: allow configuring beep frequency and duration via CLI args

def get_gas_price(rpc_url):
    """Fetch current gas price in Gwei from the Ethereum RPC."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_gasPrice",
        "params": [],
        "id": 1
    }
    r = httpx.post(rpc_url, json=payload, timeout=15)
    r.raise_for_status()
    res = r.json()
    
    # Cloudflare RPC sometimes returns error fields if rate limited
    if "error" in res:
        print(f"RPC Error response: {res['error'].get('message')}", file=sys.stderr)
        return None
        
    hex_val = res["result"]
    # print(f"DEBUG raw hex: {hex_val}")
    
    wei = int(hex_val, 16)
    return round(wei / 1_000_000_000)

def main():
    parser = argparse.ArgumentParser(
        description="Track Ethereum gas fees, send Telegram alerts and trigger system beeps."
    )
    parser.add_argument("--threshold", type=int, required=True, help="Gas threshold in Gwei")
    parser.add_argument("--interval", type=int, default=60, help="Polling interval in seconds")
    parser.add_argument("--rpc", default="https://cloudflare-eth.com", help="Ethereum RPC endpoint")
    parser.add_argument("--tg-token", help="Telegram Bot Token")
    parser.add_argument("--tg-chat", help="Telegram Chat ID")
    parser.add_argument("--cooldown", type=int, default=1800, help="Telegram alert cooldown in seconds")
    
    args = parser.parse_args()

    if (args.tg_token and not args.tg_chat) or (args.tg_chat and not args.tg_token):
        print("Error: Both --tg-token and --tg-chat must be provided for Telegram alerts.", file=sys.stderr)
        sys.exit(1)

    print(f"Tracking gas. Target: < {args.threshold} Gwei. Polling every {args.interval}s.")
    
    last_alert_Time = 0

    try:
        while True:
            try:
                gas = get_gas_price(args.rpc)
                if gas is None:
                    time.sleep(10)
                    continue
                    
                print(f"Current Gas: {gas} Gwei")
                
                if gas < args.threshold:
                    print(f"Gas is low! {gas} Gwei")
                    winsound.Beep(1000, 600)
                    
                    if args.tg_token:
                        now = time.time()
                        if now - last_alert_Time > args.cooldown:
                            msg = f"ETH Gas Alert: {gas} Gwei (Threshold: {args.threshold})"
                            send_telegram_alert(args.tg_token, args.tg_chat, msg)
                            last_alert_Time = now
                            
            except httpx.RequestError as e:
                # print short error message and keep waiting to avoid crashing the persistent loop
                print(f"Connection issue: {e}", file=sys.stderr)
            except KeyError:
                print("Error parsing RPC payload response structure", file=sys.stderr)
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\nExiting monitor loop...")
        sys.exit(0)

if __name__ == "__main__":
    main()
