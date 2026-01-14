

from fork_backend.api.router import app as fastapi_app
from fork_backend.core.db import init_db

def uvicorn_entry():
    """Factory function to create the FastAPI application."""
    init_db()
    return fastapi_app


def main():
    """Main"""
    print("Hello from fork-backend!")


if __name__ == "__main__":
    main()
