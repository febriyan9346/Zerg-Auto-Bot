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
        self.headers_base = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://welcome.zerg.app",
            "referer": "https://welcome.zerg.app/",
            "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
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
        delay = random.uniform(1.5, 3.5)
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
    
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours = i // 3600
            minutes = (i % 3600) // 60
            secs = i % 60
            print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

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

    def process_account(self, private_key_b58, proxy_url):
        signing_key, wallet_address = self.load_solana_wallet(private_key_b58)
        if not signing_key:
            return False

        wallet_short = f"{wallet_address[:8]}...{wallet_address[-8:]}"
        self.log(f"Wallet: {wallet_short}", "INFO")
        
        if proxy_url:
            self.log(f"Proxy: {proxy_url}", "INFO")
        else:
            self.log("Proxy: No Proxy", "INFO")

        session = requests.Session()
        if proxy_url:
            session.proxies = {"http": proxy_url, "https": proxy_url}

        try:
            self.log("Requesting nonce...", "INFO")
            url_nonce = "https://api-prod.zerg.app/api/v1/auth/nonce"
            res_nonce = session.post(url_nonce, headers=self.headers_base, json={"walletAddress": wallet_address}, timeout=10)
            
            if not res_nonce.ok or not res_nonce.json().get('success'):
                self.log("Failed to get nonce.", "ERROR")
                return False

            nonce_data = res_nonce.json()['data']
            nonce, message_to_sign = nonce_data['nonce'], nonce_data['message']

            self.log("Sending signature...", "INFO")
            signature = self.sign_message(signing_key, message_to_sign)
            url_verify = "https://api-prod.zerg.app/api/v1/auth/verify"
            headers_verify = self.headers_base.copy()
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
                
            time_str = self.get_wib_time()
            print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Login successful!{Style.RESET_ALL}")
            self.random_delay()

            url_me = "https://api-prod.zerg.app/api/v1/users/me"
            res_me = session.get(url_me, headers=self.headers_base, timeout=10)
            if res_me.ok and res_me.json().get('success'):
                data = res_me.json()['data']
                self.log(f"Nickname: {data.get('nickname')} | Streak: {data.get('dailyStreakCount')}", "INFO")
            self.random_delay()

            self.log("Checking Gumball status...", "INFO")
            url_gumball_status = "https://api-prod.zerg.app/api/v1/gumball/status"
            res_status = session.get(url_gumball_status, headers=self.headers_base, timeout=10)
            
            if res_status.ok and res_status.json().get('success'):
                plays_remaining = res_status.json()['data'].get('playsRemaining', 0)
                self.log(f"Tickets Remaining: {plays_remaining}", "INFO")
                
                url_gumball_play = "https://api-prod.zerg.app/api/v1/gumball/play"
                while plays_remaining > 0:
                    headers_play = self.headers_base.copy()
                    headers_play["x-idempotency-key"] = str(uuid.uuid4())
                    res_play = session.post(url_gumball_play, headers=headers_play, timeout=10)
                    
                    if res_play.ok and res_play.json().get('success'):
                        play_data = res_play.json()['data']
                        time_str = self.get_wib_time()
                        rarity = play_data.get('rarity')
                        xp_gained = play_data.get('xpAmount')
                        print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Spin: {rarity} | Reward: +{xp_gained} XP{Style.RESET_ALL}")
                        plays_remaining -= 1
                        time.sleep(1.5)
                    else:
                        self.log("Failed to spin gumball.", "ERROR")
                        break
            else:
                self.log("Failed to get Gumball status.", "WARNING")
            
            self.random_delay()

            url_xp = "https://api-prod.zerg.app/api/v1/users/me/xp"
            res_xp = session.get(url_xp, headers=self.headers_base, timeout=10)
            if res_xp.ok and res_xp.json().get('success'):
                xp_data = res_xp.json()['data']
                total_xp = xp_data.get('totalXpEarned', 0)
                rank = xp_data.get('rank', 'N/A')
                time_str = self.get_wib_time()
                print(f"[{time_str}] {Fore.GREEN}[SUCCESS] Total XP: {total_xp} | Rank: {rank}{Style.RESET_ALL}")
            
            return True

        except Exception as e:
            self.log(f"Connection error: {str(e)}", "ERROR")
            return False

    def run(self):
        self.print_banner()
        choice = self.show_menu()
        
        use_proxy = choice == '1'
        mode_text = "Running with proxy" if use_proxy else "Running without proxy"
        self.log(mode_text, "INFO")
        
        private_keys = self.load_lines(self.accounts_file)
        if not private_keys:
            self.log("No accounts found. Please add private keys.", "ERROR")
            return

        proxies = self.load_lines(self.proxy_file) if use_proxy else []
        if use_proxy and not proxies:
            self.log("Proxy mode selected but proxy.txt is empty.", "WARNING")

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
                
                proxy_to_use = proxies[i % len(proxies)] if proxies else None
                
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
