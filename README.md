# Malamal Weekly - Online Lottery & Gaming Platform

A comprehensive Django-based online lottery and gaming platform where users can participate in various gambling games, manage their wallet, and compete on leaderboards. Features a complete CMS, multiple payment gateway integrations, and a professional custom admin panel.

## 🎮 Features

### For Users
- **User Registration & Authentication**: Secure signup, login, and profile management
- **Wallet System**: Add credits, withdraw winnings, track all transactions
- **Multiple Payment Gateways**: Razorpay and Stripe integration for deposits
- **Multiple Game Types**:
  1. **Lucky Number Match**: Choose 5 numbers (0-99) in exact sequence
  2. **Super Lucky Draw**: Pick one lucky number (1-100)
  3. **Color Prediction**: Predict winning color (Red, Green, Blue, Yellow)
- **Game Participation**: Enter active game rounds with credits
- **Transaction History**: View all deposits, withdrawals, and game entries
- **Leaderboard**: Compete with other players, track rankings
- **Winners List**: See recent winners and their prizes
- **User Dashboard**: Overview of wallet, recent entries, and winnings
- **Ban Appeal System**: Users can appeal account suspensions
- **Dynamic CMS Pages**: Terms, Privacy Policy, About Us, How to Play pages

### For Admins
- **Custom Admin Panel** (`/admin-panel/`): Professional glassmorphism design
- **Dashboard**: Real-time statistics for users, games, transactions, revenue
- **Game Management**: Create, edit, delete games with custom configurations
- **Round Management**: Create game rounds, open/close for entries
- **Winner Selection**: Automated random winner selection with configurable probability
- **User Management**: View, verify, block/unblock users, manage permissions
- **Credit Management**: Approve/reject deposit and withdrawal requests
- **Transaction Oversight**: Monitor all financial transactions with filtering
- **Payment Gateway Management**: Configure Razorpay, Stripe, and other gateways
- **Ban Appeals Review**: Review and respond to user ban appeals
- **CMS Management**: Create/edit pages, manage social links, site settings
- **Modern UI**: SweetAlert2 modals, Toastr notifications, responsive design

## 📋 Prerequisites

- Python 3.8+
- MySQL 5.7+ or MariaDB 10.2+
- pip (Python package manager)
- Razorpay Account (for payment gateway integration)
- Stripe Account (optional, for alternative payment gateway)

## ✨ Key Highlights

### 💳 Payment Integration
- **Multiple Payment Gateways**: Razorpay and Stripe support
- **Real-time Payment Processing**: Instant credit addition on successful payment
- **Webhook Integration**: Automatic status updates for payment events
- **Test & Live Mode**: Switch between test and production environments
- **Payment Gateway Admin**: Configure API keys, manage multiple gateways

### 🎨 Modern UI/UX
- **Glassmorphism Design**: Beautiful frosted glass effect throughout
- **SweetAlert2 Modals**: Modern, customizable alert dialogs
- **Toastr Notifications**: Elegant toast notifications for user feedback
- **Responsive Layout**: Works seamlessly on all devices
- **Bootstrap 5**: Latest Bootstrap with custom styling
- **Dark-themed Admin**: Professional custom admin panel

### 📄 Content Management System
- **Dynamic Pages**: Create/edit pages with HTML content editor
- **Footer Management**: Organize pages into Quick Links and Information sections
- **Social Media Links**: Manage social media icons and URLs
- **Global Settings**: Site name, description, contact info, SEO settings
- **SEO Friendly**: Meta descriptions, keywords, Google Analytics integration
- **User-facing Pages**: Terms, Privacy, About Us, How to Play, etc.

### 🔧 Management Commands
- `create_initial_games`: Set up default games and admin user
- `init_cms`: Initialize CMS with default pages and settings
- `cleanup_pending_transactions`: Clean up stale pending transactions

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
pip install django pymysql Pillow razorpay stripe
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

### 6. Create Initial Games & CMS Content
```bash
python manage.py create_initial_games
python manage.py init_cms
```
This creates:
- Admin user (username: `admin`, password: `admin123`)
- 3 initial games (Lucky Number Match, Super Lucky Draw, Color Prediction)
- 5 CMS pages (About Us, How to Play, Terms & Conditions, Privacy Policy, Responsible Gaming)
- 4 social media links (Facebook, Twitter, Instagram, YouTube)
- Default site settings

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

1. **Login to Custom Admin Panel**: http://127.0.0.1:8000/admin-panel/login/
   - Username: `admin`
   - Password: `admin123`
   - **Note**: Django admin also available at http://127.0.0.1:8000/admin/

2. **Configure Payment Gateway**:
   - Navigate to **Payment Gateways**
   - Click **Add New Gateway**
   - Select provider (Razorpay/Stripe)
   - Enter API credentials
   - Set test/live mode and save

3. **Create Game Round**:
   - Go to **Games Management**
   - Select a game → **Manage Rounds**
   - Click **Create New Round**
   - Set round number, schedule start/end times
   - Save and open for entry

4. **Close Round & Select Winner**:
   - When time expires, go to round details
   - Click **Close Round for Entry**
   - Then click **Select Winner**
   - System randomly selects winner or declares no winner

5. **Approve Deposits**:
   - Go to **Deposits**
   - View pending requests with proof images
   - Click **Approve** or **Reject** with reason
   - Users get instant notifications

6. **Process Withdrawals**:
   - Go to **Withdrawals**
   - Review pending requests
   - Click **Approve** then **Complete** with transaction details
   - Or **Reject** with reason

7. **Manage CMS Content**:
   - Navigate to **CMS Pages** under Content Management
   - Create/edit pages with HTML content
   - Manage social media links
   - Update site settings globally

### User Workflow

1. **Register Account**: Create new account at /accounts/register/
2. **Add Credits**: 
   - Navigate to Wallet → Add Credits
   - Choose amount and payment method (Razorpay/Stripe)
   - Complete payment via payment gateway
   - Credits added automatically on successful payment
3. **Browse Games**: View available games and active rounds
4. **Play Game**:
   - Select a game
   - Choose your numbers/color
   - Confirm entry with SweetAlert modal
   - Credits deducted, entry confirmed via Toastr notification
5. **Check Results**: View your entries and winning status
6. **Withdraw**: Request withdrawal when you have winnings
7. **Appeal Ban**: If suspended, submit appeal from profile page

## 📁 Project Structure

```
MalamalWeekly/
├── accounts/               # User authentication & profiles
│   ├── models.py          # UserProfile, BanAppeal models
│   ├── views.py           # Login, register, profile, ban appeal views
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
│   ├── models.py          # Transaction, DepositRequest, WithdrawalRequest, PaymentGateway
│   ├── views.py           # Wallet views, Razorpay/Stripe integration
│   ├── admin.py           # Transaction admin
│   └── management/
│       └── commands/
│           └── cleanup_pending_transactions.py
├── cms/                    # Content Management System
│   ├── models.py          # Page, SocialLink, SiteSettings
│   ├── views.py           # CMS page display
│   ├── admin.py           # CMS admin interface
│   ├── context_processors.py  # Global CMS data injection
│   └── management/
│       └── commands/
│           └── init_cms.py
├── custom_admin/           # Custom admin panel
│   ├── views.py           # Dashboard, users, deposits, withdrawals, games, CMS views
│   ├── urls.py            # Admin panel routes
│   ├── context_processors.py  # Admin context data
│   └── templatetags/      # Custom template tags
├── templates/              # HTML templates
│   ├── base.html          # Base template with dynamic footer
│   ├── accounts/          # Account templates
│   ├── games/             # Game templates
│   ├── transactions/      # Transaction templates
│   ├── cms/               # CMS page templates
│   └── custom_admin/      # Custom admin panel templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # Uploaded files (deposit proofs, avatars)
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
- User blocking functionality with ban appeal system
- Transaction verification and approval workflow
- Duplicate entry prevention
- Credit validation before game entry
- Payment gateway webhook verification
- Secure payment callback handling
- Admin-only access restrictions for sensitive operations

## 🛠️ Admin Features

### Custom Admin Panel (`/admin-panel/`)
- **Professional Dashboard**: Real-time stats, charts, recent activity
- **User Management**: View all users, search, filter, block/unblock, manage permissions
- **Deposit Management**: Approve/reject with image proof viewing
- **Withdrawal Management**: Multi-step approval workflow (approve → complete)
- **Game Management**: Create/edit games, manage rounds, select winners
- **Transaction Monitoring**: View all transactions with filters
- **Payment Gateway Config**: Add/edit Razorpay, Stripe configurations
- **Ban Appeals**: Review user appeals, respond with decisions
- **CMS Management**: Create/edit pages, manage social links, site settings
- **Bulk Actions**: Process multiple requests simultaneously
- **Modern UI**: Glassmorphism design, SweetAlert2 confirmations, Toastr notifications
- **Responsive Design**: Works on desktop, tablet, and mobile

## 📊 Database Models

### Accounts App
- **UserProfile**: Extended user info with wallet, KYC status
- **BanAppeal**: User ban appeal system with admin responses

### Games App
- **Game**: Game definitions and configurations
- **GameRound**: Individual game sessions with open/closed status
- **UserEntry**: User's game participations with chosen numbers/colors
- **Winner**: Winner records with prize amounts
- **Leaderboard**: User rankings based on winnings

### Transactions App
- **Transaction**: All financial transactions (deposits, withdrawals, entries, winnings)
- **DepositRequest**: Credit addition requests with payment proofs
- **WithdrawalRequest**: Withdrawal requests with bank details
- **PaymentGateway**: Payment gateway configurations (Razorpay, Stripe)

### CMS App
- **Page**: Dynamic content pages with HTML content, SEO meta
- **SocialLink**: Social media links for footer
- **SiteSettings**: Global site settings (singleton model)

## 🎨 Technologies Used

- **Backend**: Django 5.2.7
- **Database**: MySQL with PyMySQL
- **Frontend**: Bootstrap 5, Bootstrap Icons, Custom Glassmorphism CSS
- **JavaScript Libraries**: SweetAlert2 (modals), Toastr.js (notifications)
- **Payment Gateways**: Razorpay SDK, Stripe SDK
- **Authentication**: Django Auth System
- **Image Handling**: Pillow
- **Font**: Google Fonts (Poppins)

## 📝 Recent Updates (November 2024)

- ✅ Complete CMS system with dynamic pages, social links, site settings
- ✅ Custom admin panel with professional glassmorphism design
- ✅ Razorpay and Stripe payment gateway integration
- ✅ SweetAlert2 modals replacing plain JavaScript alerts
- ✅ Toastr notifications for better UX
- ✅ Ban appeal system for suspended users
- ✅ Payment gateway management in admin panel
- ✅ Webhook handling for payment status updates
- ✅ Transaction status automation (pending → failed on cancellation)
- ✅ Dynamic footer with CMS-managed content
- ✅ Management commands for CMS initialization and transaction cleanup

## 📝 Future Enhancements

- [ ] Email notifications for game results and transactions
- [ ] SMS notifications for winners
- [ ] Automated game round scheduling with cron jobs
- [ ] Social media login (Google, Facebook)
- [ ] Referral system with rewards
- [ ] Bonus and promotional codes
- [ ] Live game results with WebSocket
- [ ] Chat support integration
- [ ] Mobile app (React Native/Flutter)
- [ ] Multi-language support
- [ ] Advanced analytics and reporting

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
