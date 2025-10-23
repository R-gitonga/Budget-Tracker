from app import create_app, db
from app.models import Category, Transaction

app = create_app()

with app.app_context():
    # delete all data
    db.session.query(Transaction).delete()
    db.session.query(Category).delete()
    db.session.commit()
    print("Database reset: all data deleted.")

# for table in reversed(db.metadata.sorted_tables):
#     db.session.execute(table.delete())
# db.session.commit() wipes data from all tables

