import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
OAUTH_AUTHORIZE_URL = os.getenv("OAUTH_AUTHORIZE_URL", "")
OAUTH_TOKEN_URL = os.getenv("OAUTH_TOKEN_URL", "")
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")
ACM_HUB_API_URL = os.getenv("ACM_HUB_API_URL", "")
ACM_HUB_CA_CERT = os.getenv("ACM_HUB_CA_CERT", "")
CLI_IMAGE = os.getenv("CLI_IMAGE", "")
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
