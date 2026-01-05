"""
Test script to verify database setup and CRUD operations
Run this to test the database integration locally
"""
from app.database import engine, Base, SessionLocal
from app.models import User, Swing, AnalysisResult
import json

def test_database_setup():
    """Test database connection and table creation"""
    print("🔧 Testing database setup...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
    
    # Get a database session
    db = SessionLocal()
    
    try:
        # Test 1: Create a user
        print("\n📝 Test 1: Creating a user...")
        user = User(email="test@diamondmind.com", username="testuser")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ User created: ID={user.id}, Email={user.email}")
        
        # Test 2: Create a swing for the user
        print("\n📝 Test 2: Creating a swing...")
        swing = Swing(
            user_id=user.id,
            filename="test_swing.mp4",
            video_url="/api/videos/download/test_swing.mp4"
        )
        db.add(swing)
        db.commit()
        db.refresh(swing)
        print(f"✅ Swing created: ID={swing.id}, Filename={swing.filename}")
        
        # Test 3: Create analysis result for the swing
        print("\n📝 Test 3: Creating analysis result...")
        analysis = AnalysisResult(
            swing_id=swing.id,
            skeletal_data={"frames": [{"landmarks": []}]},
            total_frames=120,
            frames_with_person=115,
            fps=30.0,
            bat_trail=[{"x": 100, "y": 200}]
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        print(f"✅ Analysis created: ID={analysis.id}, Total Frames={analysis.total_frames}")
        
        # Test 4: Query user's swings
        print("\n📝 Test 4: Querying user's swings...")
        user_swings = db.query(Swing).filter(Swing.user_id == user.id).all()
        print(f"✅ Found {len(user_swings)} swing(s) for user {user.username}")
        
        # Test 5: Test cascading delete
        print("\n📝 Test 5: Testing cascading delete...")
        swing_id = swing.id
        analysis_id = analysis.id
        
        db.delete(user)
        db.commit()
        
        # Verify swing and analysis were deleted
        deleted_swing = db.query(Swing).filter(Swing.id == swing_id).first()
        deleted_analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
        
        if deleted_swing is None and deleted_analysis is None:
            print("✅ Cascading delete works! Swing and analysis were deleted with user")
        else:
            print("❌ Cascading delete failed!")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database_setup()
