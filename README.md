# PyAPI (aka LilAPI 2)

FastAPI based with option to either use local or cloud db. Definitely still very much in development. Not intended for production.

Create a .env file with the following params:

```env
DATABASE_TYPE=sqlite
CLOUD_DB_URL=
CLOUD_DB_API_KEY=
SECRET_KEY=your-secret-key-change-this
ALLOWED_ORIGINS=http://localhost:8000
TEST_USER=testuser
TEST_PASSWORD=testpassword
```

Of course you should set SECRET_KEY to a secure random hash, and feel free to change the test username and password to whatever you like.
