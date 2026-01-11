from fastapi import FastAPI
from mysite.api import user, group, chat_wb, auth, chat, message, people
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from mysite.config import SECRET_KEY

chat_app = FastAPI()
chat_app.include_router(auth.auth_router)
chat_app.include_router(user.user_router)
chat_app.include_router(group.group_router)
chat_app.include_router(chat_wb.chat_router)
chat_app.include_router(chat.group_chat_router)
chat_app.include_router(message.message_router)
chat_app.include_router(people.people_router)
chat_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


if __name__ == '__main__':
    uvicorn.run(chat_app, host='127.0.0.1', port=8998)