#!/usr/bin/env python3
"""
Database seeding script.
Runs database seeders to populate initial data.
"""
import os
import sys
import argparse
import logging

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.seeders.user_seeder import UserSeeder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Available seeders
SEEDERS = {
    "user": UserSeeder,
}


def run_seeder(seeder_name: str, clear_first: bool = False, env: str = "local"):
    """
    Run a specific seeder.
    
    Args:
        seeder_name: Name of the seeder to run
        clear_first: Whether to clear existing data first
        env: Environment (local or production)
    """
    # Set environment variable
    os.environ["ENV"] = env
    
    if seeder_name not in SEEDERS:
        logger.error(f"Seeder '{seeder_name}' not found. Available seeders: {list(SEEDERS.keys())}")
        sys.exit(1)
    
    seeder_class = SEEDERS[seeder_name]
    
    try:
        logger.info(f"Running seeder: {seeder_name}")
        logger.info(f"Environment: {env}")
        logger.info(f"Clear first: {clear_first}")
        
        seeder = seeder_class()
        seeder.run(clear_first=clear_first)
        
        logger.info(f"Seeder '{seeder_name}' completed successfully")
        
    except Exception as e:
        logger.error(f"Error running seeder '{seeder_name}': {e}")
        sys.exit(1)


def run_all_seeders(clear_first: bool = False, env: str = "local"):
    """
    Run all available seeders.
    
    Args:
        clear_first: Whether to clear existing data first
        env: Environment (local or production)
    """
    logger.info("Running all seeders")
    
    for seeder_name in SEEDERS.keys():
        run_seeder(seeder_name, clear_first, env)
        logger.info(f"Completed seeder: {seeder_name}")
    
    logger.info("All seeders completed successfully")


def list_seeders():
    """List all available seeders."""
    logger.info("Available seeders:")
    for name, seeder_class in SEEDERS.items():
        logger.info(f"  - {name}: {seeder_class.__doc__ or 'No description'}")


def main():
    """Main function to parse arguments and run seeders."""
    parser = argparse.ArgumentParser(description="Database seeding management")
    parser.add_argument(
        "--env",
        choices=["local", "production"],
        default="local",
        help="Environment (default: local)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Seeding commands")
    
    # Run specific seeder
    run_parser = subparsers.add_parser("run", help="Run a specific seeder")
    run_parser.add_argument(
        "seeder",
        choices=list(SEEDERS.keys()),
        help="Name of the seeder to run"
    )
    
    # Run all seeders
    subparsers.add_parser("all", help="Run all seeders")
    
    # List seeders
    subparsers.add_parser("list", help="List available seeders")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "run":
        run_seeder(args.seeder, args.clear, args.env)
    elif args.command == "all":
        run_all_seeders(args.clear, args.env)
    elif args.command == "list":
        list_seeders()


if __name__ == "__main__":
    main() 