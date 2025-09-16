"""
User seeder for inserting sample users.
Seeds the database with initial user data.
"""
from app.models.user import User
from app.seeders.base_seeder import BaseSeeder


class UserSeeder(BaseSeeder):
    """
    User seeder class.
    Seeds the database with sample users.
    """
    
    def seed(self) -> None:
        """
        Seed the database with sample users.
        Creates Alice Smith and Bob Johnson if they don't exist.
        """
        # Sample users data
        sample_users = [
            {
                "first_name": "Alice",
                "last_name": "Smith"
            },
            {
                "first_name": "Bob", 
                "last_name": "Johnson"
            }
        ]
        
        created_count = 0
        
        for user_data in sample_users:
            # Check if user already exists
            if not self.record_exists(
                User,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"]
            ):
                # Create new user
                user = User(
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"]
                )
                
                self.db.add(user)
                created_count += 1
                
                self.log_info(f"Created user: {user_data['first_name']} {user_data['last_name']}")
            else:
                self.log_info(f"User already exists: {user_data['first_name']} {user_data['last_name']}")
        
        # Commit changes
        if created_count > 0:
            self.db.commit()
            self.log_info(f"Successfully created {created_count} users")
        else:
            self.log_info("No new users created - all sample users already exist")
        
        # Log final count
        total_users = self.count_records(User)
        self.log_info(f"Total users in database: {total_users}")
    
    def clear(self) -> None:
        """
        Clear all users from the database.
        Use with caution - this will delete all user data.
        """
        try:
            # Count users before deletion
            user_count = self.count_records(User)
            
            if user_count > 0:
                # Delete all users
                self.db.query(User).delete()
                self.db.commit()
                
                self.log_info(f"Cleared {user_count} users from database")
            else:
                self.log_info("No users to clear")
                
        except Exception as e:
            self.log_error(f"Error clearing users: {e}")
            self.db.rollback()
            raise 