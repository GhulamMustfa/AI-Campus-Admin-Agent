#!/usr/bin/env python3
"""
Seed the database with sample student data for testing
"""

import asyncio
import sys
from backend.tools import add_student
from backend.db import db_manager

async def seed_sample_data():
    """Add sample students to the database"""
    
    # Check database connection
    if not db_manager.is_connected():
        print("❌ Database not connected!")
        return False
    
    print("🌱 Seeding database with sample data...")
    
    sample_students = [
        {
            "name": "John Doe",
            "student_id": "STU001",
            "department": "Computer Science",
            "email": "john.doe@university.edu"
        },
        {
            "name": "Jane Smith",
            "student_id": "STU002", 
            "department": "Mathematics",
            "email": "jane.smith@university.edu"
        },
        {
            "name": "Bob Johnson",
            "student_id": "STU003",
            "department": "Computer Science",
            "email": "bob.johnson@university.edu"
        },
        {
            "name": "Alice Brown",
            "student_id": "STU004",
            "department": "Physics",
            "email": "alice.brown@university.edu"
        },
        {
            "name": "Charlie Wilson",
            "student_id": "STU005",
            "department": "Mathematics",
            "email": "charlie.wilson@university.edu"
        }
    ]
    
    added_count = 0
    for student in sample_students:
        try:
            result = await add_student(
                student["name"],
                student["student_id"],
                student["department"],
                student["email"]
            )
            
            if "successfully" in result.lower():
                added_count += 1
                print(f"✅ Added {student['name']} ({student['student_id']})")
            else:
                print(f"⚠️ {result}")
                
        except Exception as e:
            print(f"❌ Error adding {student['name']}: {e}")
    
    print(f"\n🎉 Seeding complete! Added {added_count} students.")
    return True

async def main():
    """Main function"""
    print("🚀 AI Campus Admin Agent - Data Seeder")
    
    try:
        await seed_sample_data()
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
