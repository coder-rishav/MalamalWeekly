# Malamal Weekly - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Run the Server
```bash
python manage.py runserver
```

### Step 2: Access Admin Panel
1. Open: http://127.0.0.1:8000/admin/
2. Login with:
   - Username: `admin`
   - Password: `admin123`

### Step 3: Create a Game Round
1. In admin panel, go to **Games → Game rounds**
2. Click **Add game round**
3. Fill in:
   - **Game**: Select "Lucky Number Match" (or any game)
   - **Round number**: 1
   - **Scheduled start**: Current date/time
   - **Scheduled end**: 1 hour from now
   - **Status**: Select "open"
4. Click **Save**

### Step 4: Register as User
1. Open: http://127.0.0.1:8000/
2. Click **Register**
3. Fill in the form and create account

### Step 5: Add Credits (For Testing)
**Option A: Through Admin**
1. Go to admin panel → **Transactions → Deposit requests**
2. Click **Add deposit request**
3. Select your user, amount: 1000, payment method: UPI
4. Save
5. Select the request, Actions → **Approve selected deposit requests**

**Option B: Manual Credit**
1. Admin panel → **Accounts → User profiles**
2. Find your user, click to edit
3. Set **Wallet balance**: 1000
4. Save

### Step 6: Play a Game
1. Login to user account
2. Go to **Games** or **Dashboard**
3. Select a game (e.g., "Lucky Number Match")
4. Enter your 5 numbers (0-99)
5. Click **Enter Game**
6. Credits will be deducted!

### Step 7: Select Winner (Admin)
1. Go to admin panel → **Games → Game rounds**
2. Select the round you created
3. Actions → **Close selected rounds**
4. Then Actions → **Select winner for closed rounds**
5. System will randomly select a winner!

### Step 8: Check Results
1. Login as user
2. Go to **My Entries** to see if you won
3. If you won, amount will be credited to wallet
4. Check **Winners** page to see all winners

## 🎮 Testing Different Game Types

### Lucky Number Match
- Entry: ₹50
- Select 5 numbers between 0-99
- Must match exact sequence
- Example: [12, 45, 67, 23, 89]

### Super Lucky Draw
- Entry: ₹20
- Select 1 number between 1-100
- Match the drawn number
- Example: [42]

### Color Prediction
- Entry: ₹10
- Select one color: red, green, blue, yellow
- Match the winning color
- Example: ["red"]

## 📊 Admin Quick Actions

### Approve Deposits
1. **Transactions → Deposit requests**
2. Select pending requests
3. Actions → **Approve selected deposit requests**

### Process Withdrawals
1. **Transactions → Withdrawal requests**
2. Select pending requests
3. Actions → **Approve selected withdrawal requests**
4. Then Actions → **Complete selected withdrawal requests**

### Verify Users
1. **Accounts → User profiles**
2. Select users
3. Actions → **Verify selected users**

### Block Users
1. **Accounts → User profiles**
2. Select users
3. Actions → **Block selected users**

### Update Leaderboard
1. **Games → Leaderboard**
2. Select all entries
3. Actions → **Update selected leaderboard entries**

## 🐛 Troubleshooting

### Database Connection Error
- Check MySQL is running
- Verify credentials in `settings.py`
- Ensure database `malamalweekly_db` exists

### Import Error: pymysql
```bash
pip install pymysql
```

### Import Error: PIL
```bash
pip install Pillow
```

### No Games Showing
```bash
python manage.py create_initial_games
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## 📝 Default Credentials

**Admin Account:**
- URL: http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

**Test User (Create your own):**
- URL: http://127.0.0.1:8000/accounts/register/

## 🎯 Next Steps

1. ✅ Create more game rounds
2. ✅ Test deposit/withdrawal flow
3. ✅ Play different games
4. ✅ Check leaderboard
5. ✅ Customize game settings
6. ✅ Add more game types
7. ✅ Integrate payment gateway
8. ✅ Deploy to production

## 📱 URLs Reference

| Page | URL |
|------|-----|
| Home | http://127.0.0.1:8000/ |
| Admin | http://127.0.0.1:8000/admin/ |
| Register | http://127.0.0.1:8000/accounts/register/ |
| Login | http://127.0.0.1:8000/accounts/login/ |
| Dashboard | http://127.0.0.1:8000/dashboard/ |
| Games | http://127.0.0.1:8000/games/ |
| My Entries | http://127.0.0.1:8000/my-entries/ |
| Leaderboard | http://127.0.0.1:8000/leaderboard/ |
| Add Credits | http://127.0.0.1:8000/transactions/add-credits/ |
| Transaction History | http://127.0.0.1:8000/transactions/history/ |

## 💡 Tips

- Always create game rounds with future scheduled times
- Open rounds for entry before scheduled start
- Close rounds after scheduled end
- Select winners only after closing rounds
- Test with small amounts first
- Check transaction history regularly
- Update leaderboard after game results

---

Happy Gaming! 🎲🎮
