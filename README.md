# Expense Tracker API

A RESTful Expense Tracker API built with FastAPI, PostgreSQL and SQLAlchemy.
The application allows authenticated users to manage their personal finances
by tracking income, expenses, budgets and recurring transactions.

The project was developed to explore backend development concepts, including
REST API design, asynchronous database operations, authentication,
authorization, database migrations, automated testing and application
architecture.

## Features

### 1. User Authentication

- User registration.
- User login.
- Password hashing using secure password-hashing utilities.
- JWT-based authentication.
- Protected API endpoints.
- User account activation and deactivation.
- User-specific data access.

### 2. Transaction Management

- Create financial transactions.
- Retrieve transactions.
- Retrieve individual transactions.
- Update existing transactions.
- Delete transactions.
- Support for income and expense transactions.
- Transaction filtering by type and date.
- Sorting and pagination.
- User-specific transaction ownership.

### 3. Financial Analytics

- Financial summary.
- Income and expense calculations.
- Balance calculations.
- Transaction counts.
- Monthly transaction analytics.
- Category-based spending analytics.
- Date-range filtering.

### 4. Budget Management

- Create budgets.
- Retrieve budgets.
- Update budgets.
- Delete budgets.
- Prevent duplicate budgets for the same category and period.
- Track spending against allocated budgets.
- Budget status monitoring.

### 5. Recurring Transactions

- Create recurring transactions.
- Support daily, weekly, monthly and yearly frequencies.
- Configure start and end dates.
- Automatically process due recurring transactions.
- Track the next scheduled execution.
- Prevent duplicate recurring transaction executions.
- Automatically deactivate expired recurring transactions.

### 6. Background Scheduling

- APScheduler integration.
- Automated daily recurring transaction processing.
- Scheduled execution using UTC.
- Application lifecycle integration.

### 7. Caching

- In-memory caching infrastructure.
- Configurable cache expiration.
- Cache retrieval and storage.
- Cache invalidation.
- User-specific cache keys.
- Reusable cache backend abstraction designed to support
  future Redis integration.

## Technology Stack

| Technology  | Purpose                           |
| ----------- | --------------------------------- |
| Python      | Programming language              |
| FastAPI     | Backend API framework             |
| PostgreSQL  | Relational database               |
| SQLAlchemy  | Object-relational mapper          |
| AsyncPG     | Asynchronous PostgreSQL driver    |
| Pydantic    | Data validation and serialization |
| Alembic     | Database migrations               |
| PyJWT       | JWT authentication                |
| pwdlib      | Password hashing                  |
| APScheduler | Background scheduling             |
| Pytest      | Automated testing                 |

## Project Structure

```text
expense-tracker-api/
│
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── v1/
│   │       └── router.py
│   │       └── endpoints/
│   │           ├── user.py
│   │           ├── transaction.py
│   │           ├── budget.py
│   │           └── recurring_transaction.py
│   │
│   ├── core/
│   │   ├── security.py
│   │   └── cache.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── transaction.py
│   │   ├── budget.py
│   │   └── recurring_transaction.py
│   │
│   ├── repositories/
│   │   ├── transaction.py
│   │   ├── budget.py
│   │   ├── user.py
│   │   └── recurring_transaction.py
│   │
│   ├── schemas/
│   │   ├── transaction.py
│   │   ├── budget.py
│   │   ├── user.py
│   │   └── recurring_transaction.py
│   │
│   ├── services/
│   │   ├── transaction.py
│   │   ├── budget.py
│   │   ├── user.py
│   │   ├── recurring_transaction.py
│   │   └── recurring_transaction_execution.py
│   │
│   ├── database.py
│   └── scheduler.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_transactions.py
│   ├── test_budgets.py
│   ├── test_recurring_transactions.py
│   ├── test_recurring_transaction_execution.py
│   └── test_cache.py
│
├── .env
├── .gitignore
├── alembic.ini
├── main.py
├── requirements.txt
└── README.md
```
