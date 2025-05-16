from database import db, app
from config import Config
from sqlalchemy import text

def check_database_connection():
    try:

        result = db.session.execute(text('SELECT 1'))
        print("✅ Подключение к базе данных успешно установлено")
        
 
        result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        
        print("\nСуществующие таблицы в базе данных:")
        for table in tables:
            print(f"- {table}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        check_database_connection() 