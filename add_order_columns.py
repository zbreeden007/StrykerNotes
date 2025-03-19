from app import create_app
from models import db

def add_order_columns():
    """Add order columns to member_project, member_task, and member_development tables."""
    app = create_app()
    with app.app_context():
        # It's a good practice to quote the column name if it's a reserved word.
        db.session.execute('ALTER TABLE member_project ADD COLUMN "order" INTEGER DEFAULT 0')
        db.session.execute('ALTER TABLE member_task ADD COLUMN "order" INTEGER DEFAULT 0')
        db.session.execute('ALTER TABLE member_development ADD COLUMN "order" INTEGER DEFAULT 0')
        db.session.commit()
        print("Successfully added order columns to member_project, member_task, and member_development tables")

if __name__ == "__main__":
    add_order_columns()


