from app import create_app, db
from app.models import Category, Goal, Transaction

app = create_app()

with app.app_context():
    print("This deletes ALL transactions, goals and categories for ALL users.")
    print("User accounts are kept.")
    if input("Type 'yes' to continue: ").strip().lower() != "yes":
        print("Cancelled. Nothing was deleted.")
        raise SystemExit(1)

    # Order matters: goals and transactions both point at categories.
    db.session.query(Goal).delete()
    db.session.query(Transaction).delete()
    db.session.query(Category).delete()
    db.session.commit()
    print("Done: transactions, goals and categories deleted.")