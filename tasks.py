from celery import shared_task

from models import User, db


@shared_task
def save_user(name, email):
    from app import app
    with app.app_context():
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
