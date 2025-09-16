#!/usr/bin/env python3
"""
Database migration script.
Handles Alembic commands for database migrations.
"""
import os
import sys
import argparse
import logging
import subprocess

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_alembic_command(command: list, env: str = "local"):
    """
    Run Alembic command with proper environment setup.
    
    Args:
        command: Alembic command as list
        env: Environment (local or production)
    """
    # Set environment variable
    os.environ["ENV"] = env
    
    # Change to migrations directory
    migrations_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "migrations")
    
    try:
        logger.info(f"Running Alembic command: {' '.join(command)}")
        logger.info(f"Environment: {env}")
        logger.info(f"Working directory: {migrations_dir}")
        
        result = subprocess.run(
            command,
            cwd=migrations_dir,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        if result.returncode != 0:
            logger.error(f"Alembic command failed with return code {result.returncode}")
            sys.exit(result.returncode)
        else:
            logger.info("Alembic command completed successfully")
            
    except Exception as e:
        logger.error(f"Error running Alembic command: {e}")
        sys.exit(1)


def create_migration(message: str, env: str = "local"):
    """Create a new migration."""
    command = ["alembic", "revision", "--autogenerate", "-m", message]
    run_alembic_command(command, env)


def upgrade_database(revision: str = "head", env: str = "local"):
    """Upgrade database to a specific revision."""
    command = ["alembic", "upgrade", revision]
    run_alembic_command(command, env)


def downgrade_database(revision: str, env: str = "local"):
    """Downgrade database to a specific revision."""
    command = ["alembic", "downgrade", revision]
    run_alembic_command(command, env)


def show_history(env: str = "local"):
    """Show migration history."""
    command = ["alembic", "history"]
    run_alembic_command(command, env)


def show_current(env: str = "local"):
    """Show current migration revision."""
    command = ["alembic", "current"]
    run_alembic_command(command, env)


def main():
    """Main function to parse arguments and run migrations."""
    parser = argparse.ArgumentParser(description="Database migration management")
    parser.add_argument(
        "--env",
        choices=["local", "production"],
        default="local",
        help="Environment (default: local)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Migration commands")
    
    # Create migration
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")
    
    # Upgrade database
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument(
        "revision",
        nargs="?",
        default="head",
        help="Target revision (default: head)"
    )
    
    # Downgrade database
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")
    
    # Show history
    subparsers.add_parser("history", help="Show migration history")
    
    # Show current
    subparsers.add_parser("current", help="Show current revision")
    
    # Initialize (create initial migration)
    subparsers.add_parser("init", help="Create initial migration for users table")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "create":
        create_migration(args.message, args.env)
    elif args.command == "upgrade":
        upgrade_database(args.revision, args.env)
    elif args.command == "downgrade":
        downgrade_database(args.revision, args.env)
    elif args.command == "history":
        show_history(args.env)
    elif args.command == "current":
        show_current(args.env)
    elif args.command == "init":
        logger.info("Creating initial migration for users table")
        create_migration("Initial migration - create users table", args.env)


if __name__ == "__main__":
    main() 