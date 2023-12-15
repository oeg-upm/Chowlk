
from app import db
from sqlalchemy.dialects.postgresql import JSON

# Schema definition
class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    input = db.Column(db.String)
    output = db.Column(db.String)
    errors = db.Column(JSON)

    # Store a new line in the database
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def __repr__(self) -> str:
        return super().__repr__()