# Malamal Weekly - Online Lottery & Gaming Platform

A comprehensive Django-based online lottery and gaming platform where users can participate in various gambling games, manage their wallet, and compete on leaderboards.

## 🎮 Features

### For Users
- **User Registration & Authentication**: Secure signup, login, and profile management
- **Wallet System**: Add credits, withdraw winnings, track all transactions
- **Multiple Game Types**:
  1. **Lucky Number Match**: Choose 5 numbers (0-99) in exact sequence
  2. **Super Lucky Draw**: Pick one lucky number (1-100)
  3. **Color Prediction**: Predict winning color (Red, Green, Blue, Yellow)
- **Game Participation**: Enter active game rounds with credits
- **Transaction History**: View all deposits, withdrawals, and game entries
- **Leaderboard**: Compete with other players, track rankings
- **Winners List**: See recent winners and their prizes
- **User Dashboard**: Overview of wallet, recent entries, and winnings

### For Admins
- **Game Management**: Create, edit, delete games with custom configurations
- **Round Management**: Create game rounds, open/close for entries
- **Winner Selection**: Automated random winner selection with configurable probability
- **User Management**: View, verify, block/unblock users
- **Credit Management**: Approve/reject deposit and withdrawal requests
- **Transaction Oversight**: Monitor all financial transactions
- **Statistics**: Track game performance, user activity

## 📋 Prerequisites

- Python 3.8+
- MySQL 5.7+ or MariaDB 10.2+
- pip (Python package manager)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/coder-rishav/MalamalWeekly.git
cd MalamalWeekly
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install django pymysql Pillow
```

### 4. Database Setup

**Create MySQL Database:**
```sql
CREATE DATABASE malamalweekly_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Update Database Credentials in `MalamalWeekly/settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'malamalweekly_db',
        'USER': 'your_mysql_username',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Initial Games
```bash
python manage.py create_initial_games
```
This creates:
- Admin user (username: `admin`, password: `admin123`)
- 3 initial games (Lucky Number Match, Super Lucky Draw, Color Prediction)

### 7. Create Superuser (Optional, if not using default admin)
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## 🎯 Usage Guide

### Admin Workflow

1. **Login to Admin Panel**: http://127.0.0.1:8000/admin/
   - Username: `admin`
   - Password: `admin123`

2. **Create Game Round**:
   - Go to **Games → Game rounds**
   - Click **Add game round**
   - Select game, set round number, schedule start/end times
   - Save

3. **Open Round for Entry**:
   - Select the round(s)
   - Actions → **Open selected rounds for entry**

4. **Close Round & Select Winner**:
   - When time expires, select round(s)
   - Actions → **Close selected rounds**
   - Then Actions → **Select winner for closed rounds**
   - System randomly selects winner or declares no winner

5. **Approve Deposits**:
   - Go to **Transactions → Deposit requests**
   - Select pending requests
   - Actions → **Approve selected deposit requests**

6. **Process Withdrawals**:
   - Go to **Transactions → Withdrawal requests**
   - Actions → **Approve** then **Complete selected withdrawal requests**

### User Workflow

1. **Register Account**: Create new account at /accounts/register/
2. **Add Credits**: 
   - Navigate to Wallet → Add Credits
   - Submit deposit request (admin will approve)
3. **Browse Games**: View available games and active rounds
4. **Play Game**:
   - Select a game
   - Choose your numbers/color
   - Confirm entry (credits will be deducted)
5. **Check Results**: View your entries and winning status
6. **Withdraw**: Request withdrawal when you have winnings

## 📁 Project Structure

```
MalamalWeekly/
├── accounts/               # User authentication & profiles
│   ├── models.py          # UserProfile model
│   ├── views.py           # Login, register, profile views
│   ├── forms.py           # User forms
│   └── admin.py           # User admin interface
├── games/                  # Game logic
│   ├── models.py          # Game, GameRound, UserEntry, Winner, Leaderboard
│   ├── views.py           # Game views
│   ├── admin.py           # Game admin with winner selection
│   └── management/
│       └── commands/
│           └── create_initial_games.py
├── transactions/           # Financial transactions
│   ├── models.py          # Transaction, DepositRequest, WithdrawalRequest
│   ├── views.py           # Wallet views
│   └── admin.py           # Transaction admin
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── accounts/          # Account templates
│   ├── games/             # Game templates
│   └── transactions/      # Transaction templates
├── static/                 # Static files
├── media/                  # Uploaded files
└── MalamalWeekly/         # Project settings
    ├── settings.py
    ├── urls.py
    └── __init__.py
```

## 🎲 Game Types

### 1. Lucky Number Match
- **Entry Fee**: ₹50
- **Prize**: ₹10,000
- **How to Play**: Select 5 numbers (0-99) in exact sequence
- **Winning**: Match all 5 numbers in correct order

### 2. Super Lucky Draw
- **Entry Fee**: ₹20
- **Prize**: ₹5,000
- **How to Play**: Pick one number (1-100)
- **Winning**: Match the drawn number

### 3. Color Prediction
- **Entry Fee**: ₹10
- **Prize**: ₹2,000
- **How to Play**: Choose Red, Green, Blue, or Yellow
- **Winning**: Match the winning color

## 🔐 Security Features

- Password hashing with Django's built-in authentication
- CSRF protection on all forms
- Login required decorators for protected views
- User blocking functionality
- Transaction verification
- Duplicate entry prevention
- Credit validation before game entry

## 🛠️ Admin Features

- Custom admin dashboard
- Bulk actions for user management
- Automated winner selection algorithm
- Transaction approval workflow
- Game round scheduling
- User statistics and leaderboard management

## 📊 Database Models

- **UserProfile**: Extended user info with wallet
- **Game**: Game definitions and configurations
- **GameRound**: Individual game sessions
- **UserEntry**: User's game participations
- **Winner**: Winner records
- **Leaderboard**: User rankings
- **Transaction**: All financial transactions
- **DepositRequest**: Credit addition requests
- **WithdrawalRequest**: Withdrawal requests

## 🎨 Technologies Used

- **Backend**: Django 5.2.7
- **Database**: MySQL with PyMySQL
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Authentication**: Django Auth System
- **Image Handling**: Pillow

## 📝 Future Enhancements

- [ ] Payment gateway integration (Razorpay, PayU)
- [ ] Email notifications for results
- [ ] SMS notifications
- [ ] Automated game round scheduling
- [ ] Mobile responsive improvements
- [ ] Social media login
- [ ] Referral system
- [ ] Bonus and promotional codes
- [ ] Live game results
- [ ] Chat support

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes.

## 👨‍💻 Author

**Rishav Mandal**
- Email: coder.rishav@gmail.com
- GitHub: [@coder-rishav](https://github.com/coder-rishav)

## ⚠️ Disclaimer

This is a demo project for educational purposes. Online gambling may be regulated or prohibited in your jurisdiction. Please check local laws before deploying.

---

**Happy Gaming! 🎮🎲**
