# 🤖 Zerg Auto Bot

Automated bot for [Zerg App](https://welcome.zerg.app/referral/CYQG7XOMWR) — auto login, daily streak, gumball spin, and XP tracking using Solana wallet private keys.

> 🔗 Register here: [https://welcome.zerg.app/referral/CYQG7XOMWR](https://welcome.zerg.app/referral/CYQG7XOMWR)

---

## ✨ Features

- ✅ Auto login with Solana wallet signature
- 🎰 Auto spin Gumball (uses all available tickets)
- 📊 Display total XP & rank
- 👤 Show nickname & daily streak
- 🔄 Auto cycle every 24 hours
- 🌐 Proxy support (optional)
- 🎨 Colored terminal output

---

## 📋 Requirements

- Python 3.8+
- pip packages (see below)

---

## 📦 Installation

```bash
git clone https://github.com/febriyan9346/Zerg-Auto-Bot.git
cd Zerg-Auto-Bot
pip install -r requirements.txt
```

### Install dependencies manually:

```bash
pip install requests pytz base58 PyNaCl colorama
```

---

## ⚙️ Configuration

### 1. `accounts.txt`
Add your Solana wallet **private keys** (Base58 format), one per line:

```
YourPrivateKey1Here
YourPrivateKey2Here
```

### 2. `proxy.txt` *(optional)*
Add proxies in the following format, one per line:

```
http://user:pass@host:port
http://host:port
```

---

## 🚀 Usage

```bash
python bot.py
```

You will be prompted to select a mode:

```
1. Run with proxy
2. Run without proxy
```

---

## 📁 File Structure

```
Zerg-Auto-Bot/
├── bot.py           # Main bot script
├── accounts.txt     # Solana private keys (create this)
├── proxy.txt        # Proxy list (optional)
├── requirements.txt # Python dependencies
└── README.md
```

---

## ⚠️ Disclaimer

This bot is for **educational purposes only**. Use at your own risk. The author is not responsible for any misuse or account bans.

---

## 📄 License

MIT License © 2025 FEBRIYAN

---

## 💰 Support Us with Cryptocurrency

You can make a contribution using any of the following blockchain networks:

| Network | Wallet Address |
|---------|---------------|
| **EVM** | `0x216e9b3a5428543c31e659eb8fea3b4bf770bdfd` |
| **TON** | `UQCEzXLDalfKKySAHuCtBZBARCYnMc0QsTYwN4qda3fE6tto` |
| **SOL** | `9XgbPg8fndBquuYXkGpNYKHHhymdmVhmF6nMkPxhXTki` |
| **SUI** | `0x8c3632ddd46c984571bf28f784f7c7aeca3b8371f146c4024f01add025f993bf` |
