
import os
import sys
import logging
from sqlalchemy import create_engine, MetaData, Table, select, insert, text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_data():
    """
    Migrate data from Remote (Render) DB to Local (Postgres) DB.
    Handles Enum -> String conversion for 'swings' table.
    """
    
    # 1. Configuration
    # LOCAL DB (Target)
    LOCAL_DB_URL = "postgresql://diamond_user:dev_password_change_in_production@localhost:5432/diamondmind"
    
    # REMOTE DB (Source) - PLACEHOLDER
    # User needs to provide this!
    REMOTE_DB_URL = input("Enter Render Database URL (e.g. postgresql://user:pass@host/db): ").strip()
    
    if not REMOTE_DB_URL:
        logger.error("❌ No Remote DB URL provided. Exiting.")
        return

    logger.info("🚀 Starting Migration: Remote -> Local")

    # 2. Connect to Databases
    try:
        source_engine = create_engine(REMOTE_DB_URL)
        target_engine = create_engine(LOCAL_DB_URL)
        
        source_conn = source_engine.connect()
        target_conn = target_engine.connect()
        logger.info("✅ Connected to both databases.")
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return

    # 3. Define Tables (using Reflection to get source schema)
    metadata = MetaData()
    
    try:
        # Reflect Source Tables
        logger.info("🔍 Reflecting source tables...")
        metadata.reflect(bind=source_engine)
        
        users_table = metadata.tables.get('users')
        swings_table = metadata.tables.get('swings')
        analysis_table = metadata.tables.get('analysis_results')
        
        if users_table is None:
             logger.error("❌ 'users' table not found in source DB.")
             return

        # 3.5 CLEANUP LOCAL DB
        print("\n⚠️  WARNING: This will WIPE user/swing data from the LOCAL database to prevent conflicts.")
        if input("Type 'yes' to proceed with wiping local data: ").lower().strip() == 'yes':
            logger.info("🧹 Wiping local tables...")
            try:
                # Disable FK checks temporarily or just cascade truncate? Postgres requires CASCADE.
                target_conn.execute(text("TRUNCATE TABLE users, swings, analysis_results RESTART IDENTITY CASCADE"))
                target_conn.commit()
                logger.info("✅ Local tables wiped.")
            except Exception as e:
                logger.error(f"❌ Failed to wipe local tables: {e}")
                return
        else:
            logger.info("ℹ️ Skipping wipe (Duplicate Key errors may occur).")

        # 4. Migrate Users
        logger.info("👤 Migrating Users...")
        # Clear local users first? No, let's use ON CONFLICT DO NOTHING logic (or check existence)
        # For simplicity in this script, we'll try to insert and ignore specific duplicates if needed,
        # but standard SQL copy is easiest.
        
        # Pull all source users
        stmt = select(users_table)
        source_users = source_conn.execute(stmt).fetchall()
        logger.info(f"   Found {len(source_users)} users in source.")
        
        # Insert into target
        # mapping columns manually to ensure Enum->String conversion if needed
        # Users table Enums: age_group, handedness (might be Enum objects in source, String in target)
        
        count_users = 0
        for row in source_users:
            user_data = row._mapping
            
            # Check if user exists locally (by email or supabase_id)
            exists_query = text("SELECT id FROM users WHERE email = :email")
            exists = target_conn.execute(exists_query, {"email": user_data['email']}).fetchone()
            
            if not exists:
                # Prepare data dict
                insert_data = dict(user_data)
                
                # Convert Enums to strings if they aren't already
                if hasattr(insert_data.get('age_group'), 'value'):
                     insert_data['age_group'] = insert_data['age_group'].value
                
                if hasattr(insert_data.get('handedness'), 'value'):
                     insert_data['handedness'] = insert_data['handedness'].value
                     
                # Remove 'id' to let local DB auto-increment? 
                # NO, we must preserve IDs to keep relationships valid!
                
                # Construct INSERT statement manually to handle raw SQL execution for safety
                # But sqlalchemy core is better.
                # However, we need to handle potential 'id' conflicts if local DB is not empty.
                # User said local DB is likely empty/no user data.
                
                try:
                    # Using table object from reflection on target? No, target schema might differ (String vs Enum)
                    # Use text insert for maximum control
                    cols = insert_data.keys()
                    # Filter out None keys if any
                    
                    # Safe insert
                    # We assume target table structure matches keys. 
                    # Let's map explicitly needed fields.
                    
                    target_conn.execute(
                        text("""
                        INSERT INTO users (id, supabase_id, email, username, age_group, handedness, height_cm, created_at, updated_at)
                        VALUES (:id, :supabase_id, :email, :username, :age_group, :handedness, :height_cm, :created_at, :updated_at)
                        """),
                        insert_data
                    )
                    count_users += 1
                except Exception as e:
                    logger.warning(f"   Skiamping user {user_data['email']}: {e}")
            else:
                 logger.info(f"   Skipping existing user: {user_data['email']}")
                 
        target_conn.commit()
        logger.info(f"✅ Migrated {count_users} Users.")

        # 5. Migrate Swings
        if swings_table is not None:
            logger.info("⚾ Migrating Swings...")
            stmt = select(swings_table)
            source_swings = source_conn.execute(stmt).fetchall()
            logger.info(f"   Found {len(source_swings)} swings in source.")
            
            count_swings = 0
            for row in source_swings:
                swing_data = dict(row._mapping)
                
                # Check exist
                exists = target_conn.execute(text("SELECT id FROM swings WHERE id = :id"), {"id": swing_data['id']}).fetchone()
                if not exists:
                    # Fix Enum: status
                    if hasattr(swing_data.get('status'), 'value'):
                        swing_data['status'] = swing_data['status'].value
                    # Ensure status is string even if it was just a string object
                    swing_data['status'] = str(swing_data['status'])
                    
                    try:
                        target_conn.execute(
                            text("""
                            INSERT INTO swings (id, user_id, filename, video_url, status, error_message, title, notes, created_at)
                            VALUES (:id, :user_id, :filename, :video_url, :status, :error_message, :title, :notes, :created_at)
                            """),
                            swing_data
                        )
                        count_swings += 1
                    except Exception as e:
                        logger.warning(f"   Failed to migrate swing {swing_data['id']}: {e}")

            target_conn.commit()
            logger.info(f"✅ Migrated {count_swings} Swings.")
        
        # 6. Migrate Analysis Results
        if analysis_table is not None:
             import json
             logger.info("📊 Migrating Analysis Results...")
             stmt = select(analysis_table)
             source_analysis = source_conn.execute(stmt).fetchall()
             logger.info(f"   Found {len(source_analysis)} analysis records.")
             
             count_analysis = 0
             for row in source_analysis:
                 res_data = dict(row._mapping)
                 
                 exists = target_conn.execute(text("SELECT id FROM analysis_results WHERE id = :id"), {"id": res_data['id']}).fetchone()
                 if not exists:
                     try:
                        # SERIALIZATION FIX: Convert dicts/lists to JSON strings
                        for json_col in ['skeletal_data', 'bat_trail', 'feedback']:
                            if res_data.get(json_col) is not None:
                                # Ensure we don't double-encode strings
                                if not isinstance(res_data[json_col], str):
                                    res_data[json_col] = json.dumps(res_data[json_col])
                        
                        target_conn.execute(
                            text("""
                            INSERT INTO analysis_results (id, swing_id, skeletal_data, total_frames, frames_with_person, fps, bat_trail, phase, score, feedback, drill, drill_explanation, created_at)
                            VALUES (:id, :swing_id, :skeletal_data, :total_frames, :frames_with_person, :fps, :bat_trail, :phase, :score, :feedback, :drill, :drill_explanation, :created_at)
                            """),
                            res_data
                        )
                        target_conn.commit() # Commit each to isolate failures
                        count_analysis += 1
                     except Exception as e:
                         target_conn.rollback() # Rollback singular failure
                         logger.warning(f"   Failed to migrate analysis {res_data['id']}: {e}")
             
             logger.info(f"✅ Migrated {count_analysis} Analysis Results.")
             
        # 7. Reset Sequences
        # Important! Since we inserted IDs manually, the auto-increment sequences needs to be updated.
        logger.info("🔄 Resetting ID sequences...")
        target_conn.execute(text("SELECT setval(pg_get_serial_sequence('users', 'id'), coalesce(max(id),0) + 1, false) FROM users;"))
        target_conn.execute(text("SELECT setval(pg_get_serial_sequence('swings', 'id'), coalesce(max(id),0) + 1, false) FROM swings;"))
        target_conn.execute(text("SELECT setval(pg_get_serial_sequence('analysis_results', 'id'), coalesce(max(id),0) + 1, false) FROM analysis_results;"))
        target_conn.commit()
        logger.info("✅ Sequences reset.")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
    finally:
        source_conn.close()
        target_conn.close()
        logger.info("🏁 Migration process finished.")

if __name__ == "__main__":
    migrate_data()
