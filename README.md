# E-Voting System

An online voting system developed with Django. This system is designed to enhance the transparency, security, and accessibility of voting processes within institutions and organizations.

## 🚀 Features

- ✅ **Voter Registration** – Voters are registered and verified by staff before voting.
- ✅ **Admin Panel** – Super admin can:
  - Add and manage candidates
  - View total voters and votes per candidate
- ✅ **Eligibility Check** – Prevents multiple voting and ensures only verified users vote.
- ✅ **Secure Vote Casting** – Votes are stored securely with constraints to avoid duplication.
- ✅ **Result Display** – Real-time display of results per candidate.
- ✅ **Staff Roles** – Assigned roles for voter verification and registration.
- 🔐 **Future Integration Plans**:
  - AI analytics on voting patterns
  - OTP verification via SMS 
  - Blockchain record validation

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS,Js
- **Database:** SQLite 
- **Version Control:** Git + GitHub

## ⚙️ Installation

```bash
git clone https://github.com/Kim-254-de/VotingSystem.git
cd VotingSystem
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
