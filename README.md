# Sardoba Restaurant Telegram Bot

## Docker (Tavsiya)

### 1) Talablar
- Docker Desktop o'rnatilgan bo'lsin

### 2) .env sozlash
`.env` ichida kamida shu qiymatlar bo'lsin:
- `TELEGRAM_BOT_TOKEN=...`
- `GROUP_CHAT_ID=-100...` (guruh ID)

Eslatma: Docker compose ichida DB parametrlari avtomatik `db` servisi bilan ishlaydi.

### 3) Ishga tushirish
PowerShell:
```powershell
cd c:\xampp\htdocs\bot1
docker compose up -d --build
```

### 4) Log ko'rish
```powershell
docker compose logs -f bot
```

### 5) phpMyAdmin (ixtiyoriy)
Brauzer: `http://localhost:8080`
- login: `root`
- password: `root`

### 6) To'xtatish
```powershell
docker compose down
```

This is a comprehensive Telegram bot for managing restaurant operations with two user roles: Admin and Cashier.

## Features

### For Cashiers:
- Shift opening and closing
- Location selection (4 branches)
- Workplace status reporting with photos
- Daily reporting (sales, debts, expenses, card payments, etc.)
- Shift reconciliation process

### For Admins:
- Manage all cashiers
- Monitor shift openings/closings
- Generate reports
- Approve cashier requests
- Modify information
- Export data to Excel/PDF

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bot1
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
mysql -u root -p < database_schema.sql
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Telegram bot token and database credentials
```

5. Run the bot:
```bash
python bot.py
```

## Configuration

Create a `.env` file with the following variables:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Database Configuration
DB_HOST=localhost
DB_NAME=sardoba_bot
DB_USER=root
DB_PASSWORD=
DB_PORT=3306
```

## Database Schema

The bot uses the following tables:
- `users` - stores admin and cashier information
- `locations` - restaurant branch locations
- `shifts` - tracks cashier shifts
- `reports` - daily reports and financial data
- `images` - uploaded images for reports
- `approval_requests` - cashier registration requests

## Usage

1. Start the bot with `/start`
2. Select language (Uzbek/Russian)
3. Select role (Admin/Cashier)
4. Register with personal information and password
5. For cashiers, wait for admin approval
6. Use the appropriate menu based on your role

### For Cashiers:
- Open shift with opening amount
- Upload required photos of workplace status
- Submit daily reports (sales, debts, expenses, etc.)
- Close shift when finished

### For Admins:
- View all cashiers
- Monitor shift activity
- Review and approve cashier requests
- Generate and export reports

## File Structure

```
bot1/
├── bot.py              # Main bot implementation
├── db_config.py        # Database connection utilities
├── utils.py            # Utility functions (password hashing, validation)
├── export_utils.py     # Excel/PDF export functionality
├── requirements.txt    # Python dependencies
├── database_schema.sql # Database schema
├── .env               # Environment variables
└── README.md          # This file
```

## Technologies Used

- Python 3.x
- python-telegram-bot
- MySQL
- pandas (for Excel exports)
- reportlab (for PDF generation)

## Security Features

- Password hashing with salt
- Input validation
- Role-based access control
- Secure database connections

## License

This project is licensed under the MIT License.
