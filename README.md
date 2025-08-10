# 🤖 Urex Bot – Tissemsilt Science Club

## 📌 Overview
**Urex Bot** is a Telegram bot designed to manage the activities of the Urex Science Club at Tissemsilt University.  
It allows members and guests to browse upcoming events, view important announcements, submit feedback, and interact with the administration.  
The bot supports a **role-based access system** with an advanced admin panel.

---

## ✨ Features
- 🔐 **Secure Login** using username and password.
- 📅 **Event Management**:
  - View upcoming, ongoing, completed, and canceled events.
  - Register or unregister for events.
  - Add, edit, or delete events (for moderators/admins only).
- 📢 **Announcement Management**:
  - Add, delete, and pin announcements.
  - Set priority (high – medium – low).
- 👥 **User Management**:
  - View member list and their roles.
  - Change permissions (admins only).
- 📊 **Statistics**:
  - Insights on members, events, and announcements.
- ✍️ **Feedback System**:
  - Submit suggestions or comments directly to the club administration.
- 📌 **Role Support**:
  - **Admin** – Full control.
  - **Moderator** – Control events and announcements.
  - **Member** – Browse and participate.
  - **Guest** – Limited access.

---

## 🛠️ Tech Stack
- **Python 3**
- [python-telegram-bot](https://python-telegram-bot.org/)
- **PicklePersistence** – Persistent session data storage.
- **Logging** – Activity and error tracking.
- **Enums & Dataclasses** – For state and role management.

---

## 📦 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/username/urex-bot.git
cd urex-bot
```

### 2️⃣ Create a virtual environment & install dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ Configure the bot token
- Create a bot via [BotFather](https://t.me/BotFather) on Telegram.
- Copy your **TOKEN** and place it inside `Urex.py`:
```python
updater = Updater("YOUR_BOT_TOKEN", persistence=persistence, use_context=True)
```

---

## 🚀 Usage
```bash
python Urex.py
```
Once running, open Telegram and send:
```
/start
```

---

## 📂 Project Structure
```
Urex/
│
├── Urex.py               # Main bot code
├── requirements.txt      # Dependencies
└── README.md              # This file
```

---

## 💡 How to Use
1. Log in with your username and password.
2. Use the main menu to browse:
   - Events
   - Announcements
   - Club info
   - Contact the administration
3. For members with privileges:
   - Access the admin panel to manage content.

---

## 🐞 Error Handling
- Clear user alerts when errors occur.
- Logs all errors in `urex_bot.log`.

---

## 🤝 Contributing
- Fork the project.
- Create a new branch: `git checkout -b feature-name`.
- Make your changes.
- Submit a **Pull Request**.

---

## 📜 License
This project is open-source under the MIT License – free to use and modify.
