from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def delete_old_files(cls):
        # Delete files uploaded more than 24 hours ago
        older_than_24h = datetime.utcnow() - timedelta(hours=24)
        cls.query.filter(cls.upload_time < older_than_24h).delete()
        db.session.commit()
