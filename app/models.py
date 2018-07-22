from app import db

user_info_assignment = db.Table(
    "user_info_assigment",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("info_id", db.Integer, db.ForeignKey("info.id"))
)

class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)

    def __str__(self):
        return "<Info %s:%s>" % (self.key, self.value)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    info = db.relationship(
        "Info", 
        backref="user", 
        lazy="dynamic", 
        cascade="all,delete", 
        secondary=user_info_assignment
    )

    def __str__(self):
        return "<User %s>" % self.name