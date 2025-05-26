import uuid
from .model import Session
from datetime import datetime, timedelta
from src.redis_untils.service import getRedisclient
from src.__utils.env import env
import logging

def createSessionId():
    session_id = str(uuid.uuid4())
    return session_id

async def insertNewSession(user_id: str, session_id: str):
    session = Session(
        session_id=session_id,
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(seconds=env.session_expire_seconds)
    )
    data = session.save()
    result = data.expire(num_seconds=env.session_expire_seconds)




# def get_session(session_id: str):
#     sessions = list(Session.find(Session.session_id == session_id))
#     if not sessions:s
#         raise HTTPException(status_code=401, detail="Session not found")

#     session = sessions[0]
#     if session.expires_at < datetime.utcnow():
#         Session.delete(session.pk)
#         raise HTTPException(status_code=401, detail="Session expired")

#     return session.user_id