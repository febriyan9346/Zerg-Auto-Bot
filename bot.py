import os
import time
import random
import uuid
import sys
import warnings
from datetime import datetime
import pytz
import requests
import base58
import nacl.signing
from colorama import Fore, Style, init

os.system('clear' if os.name == 'posix' else 'cls')
warnings.filterwarnings('ignore')

if not sys.warnoptions:
    os.environ["PYTHONWARNINGS"] = "ignore"

init(autoreset=True)


class ZergBot:
    def __init__(self):
        self.accounts_file = "accounts.txt"
        self.proxy_file = "proxy.txt"
        self.api_base = "https://api-prod.zerg.app/api/v1"
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "origin": "https://zerg.app",
            "referer": "https://zerg.app/",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/148.0.0.0 Safari/537.36"
            ),
        }

    def get_wib_time(self):
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime('%H:%M:%S')

    def print_banner(self):
        banner = f"""
{Fore.CYAN}ZERG AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
"""
        print(banner)

    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()

        if level == "INFO":
            color = Fore.CYAN
            symbol = "[INFO]"
        elif level == "SUCCESS":
            color = Fore.GREEN
            symbol = "[SUCCESS]"
        elif level == "ERROR":
            color = Fore.RED
            symbol = "[ERROR]"
        elif level == "WARNING":
            color = Fore.YELLOW
            symbol = "[WARNING]"
        elif level == "CYCLE":
            color = Fore.MAGENTA
            symbol = "[CYCLE]"
        else:
            color = Fore.WHITE
            symbol = "[LOG]"

        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")

    def random_delay(self):
        delay = random.randint(1, 3)
        self.log(f"Delay {delay} seconds...", "INFO")
        time.sleep(delay)

    def show_menu(self):
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Run with proxy")
        print(f"2. Run without proxy{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")

        while True:
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
                if choice in ['1', '2']:
                    return choice
                else:
                    print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}Program terminated by user.{Style.RESET_ALL}")
                exit(0)

    def load_lines(self, filename):
        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            return lines
        except FileNotFoundError:
            self.log(f"File {filename} not found.", "ERROR")
            return []

    def load_solana_wallet(self, private_key_b58):
        try:
            key_bytes = base58.b58decode(private_key_b58)
            seed = key_bytes[:32]
            signing_key = nacl.signing.SigningKey(seed)
            wallet_address = base58.b58encode(signing_key.verify_key.encode()).decode('utf-8')
            return signing_key, wallet_address
        except Exception as e:
            self.log(f"Error parsing private key: {e}", "ERROR")
            return None, None

    def sign_message(self, signing_key, message):
        signed = signing_key.sign(message.encode('utf-8'))
        signature = base58.b58encode(signed.signature).decode('utf-8')
        return signature

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours = i // 3600
            minutes = (i % 3600) // 60
            secs = i % 60
            print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    def process_account(self, private_key_b58, proxy_url):
        signing_key, wallet_address = self.load_solana_wallet(private_key_b58)
        if not signing_key:
            return False

        wallet_short = f"{wallet_address[:8]}...{wallet_address[-8:]}"

        if proxy_url:
            self.log(f"Proxy: {proxy_url}", "INFO")
        else:
            self.log("Proxy: No Proxy", "INFO")

        self.log(f"{wallet_short}", "INFO")

        session = requests.Session()
        if proxy_url:
            session.proxies = {"http": proxy_url, "https": proxy_url}

        try:
            # Step 1: Get nonce
            self.log("Requesting nonce...", "INFO")
            url_nonce = f"{self.api_base}/handshake/start"
            res_nonce = session.post(url_nonce, headers=self.headers, json={"walletAddress": wallet_address}, timeout=10)

            if not res_nonce.ok or not res_nonce.json().get('success'):
                self.log(f"Failed to get nonce: {res_nonce.text}", "ERROR")
                return False

            nonce_data = res_nonce.json()['data']
            nonce, message_to_sign = nonce_data['nonce'], nonce_data['message']

            # Step 2: Sign & confirm
            self.log("Sending signature...", "INFO")
            signature = self.sign_message(signing_key, message_to_sign)
            url_verify = f"{self.api_base}/handshake/confirm"
            headers_verify = self.headers.copy()
            headers_verify["x-idempotency-key"] = str(uuid.uuid4())

            payload_verify = {
                "message": message_to_sign,
                "nonce": nonce,
                "signature": signature,
                "walletAddress": wallet_address
            }
            res_verify = session.post(url_verify, headers=headers_verify, json=payload_verify, timeout=10)

            if not res_verify.ok or not res_verify.json().get('success'):
                self.log(f"Login failed: {res_verify.text}", "ERROR")
                return False

            set_cookie = res_verify.headers.get('set-cookie', '')
            if 'auth_token=' in set_cookie:
                self.log("Token set via Set-Cookie header", "INFO")

            time_str = self.get_wib_time()
            print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Login successful!{Style.RESET_ALL}")
            self.random_delay()

            # Step 3: Check inventory
            self.log("Checking inventory...", "INFO")
            url_inventory = f"{self.api_base}/dispenser/inventory"
            res_inv = session.get(url_inventory, headers=self.headers, timeout=10)
            if res_inv.ok and res_inv.json().get('success'):
                inv = res_inv.json()['data']
                plays_left = inv.get('playsRemaining', 0)
                plays_limit = inv.get('dailyLimit', 0)
                self.log(f"Plays Remaining: {plays_left}/{plays_limit}", "INFO")
            else:
                self.log(f"Failed to check inventory: {res_inv.status_code}", "WARNING")
                return False

            # Step 4: Spin
            self.log("Processing Spins...", "INFO")
            url_dispense = f"{self.api_base}/dispenser/pull"
            spin_count = 0
            total_xp = 0
            max_spins = 50

            while spin_count < max_spins:
                headers_dispense = self.headers.copy()
                headers_dispense["x-idempotency-key"] = str(uuid.uuid4())

                res_dispense = session.post(url_dispense, headers=headers_dispense, json={}, timeout=10)

                if res_dispense.ok and res_dispense.json().get('success'):
                    play_data = res_dispense.json()['data']
                    time_str = self.get_wib_time()
                    rarity = play_data.get('rarity')
                    xp_gained = play_data.get('xpAmount', 0)
                    total_xp += xp_gained
                    spin_count += 1
                    print(f"[{time_str}] {Fore.GREEN}[SPIN #{spin_count}] {rarity} | +{xp_gained} XP{Style.RESET_ALL}")
                    time.sleep(1.5)
                else:
                    break

            if spin_count > 0:
                time_str = self.get_wib_time()
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Total Spins: {spin_count} | XP Earned: +{total_xp}{Style.RESET_ALL}")
            else:
                self.log("No spins available", "WARNING")

            self.random_delay()

            return True

        except Exception as e:
            self.log(f"Connection error: {str(e)}", "ERROR")
            return False

    def run(self):
        self.print_banner()

        choice = self.show_menu()

        use_proxy = choice == '1'
        proxies = self.load_lines(self.proxy_file) if use_proxy else []

        if use_proxy:
            if not proxies:
                self.log("Proxy mode selected but proxy.txt is empty.", "WARNING")
                self.log("Falling back to no proxy", "WARNING")
                use_proxy = False
            else:
                self.log("Running with proxy", "INFO")
        else:
            self.log("Running without proxy", "INFO")

        private_keys = self.load_lines(self.accounts_file)
        if not private_keys:
            self.log("No accounts found. Please add private keys.", "ERROR")
            return

        self.log(f"Loaded {len(private_keys)} accounts successfully", "INFO")
        print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

        cycle = 1
        while True:
            self.log(f"Cycle #{cycle} Started", "CYCLE")
            print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")

            success_count = 0
            total_accounts = len(private_keys)

            for i, pk in enumerate(private_keys):
                self.log(f"Account #{i+1}/{total_accounts}", "INFO")

                proxy_to_use = proxies[i % len(proxies)] if proxies and use_proxy else None

                if self.process_account(pk, proxy_to_use):
                    success_count += 1

                if i < total_accounts - 1:
                    print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                    time.sleep(2)

            print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
            self.log(f"Cycle #{cycle} Complete | Success: {success_count}/{total_accounts}", "CYCLE")
            print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")

            cycle += 1
            self.countdown(86400)


if __name__ == "__main__":
    bot = ZergBot()
    bot.run()
