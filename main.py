import uvicorn
from dotenv import load_dotenv

load_dotenv()


# from fastapi import FastAPI
# from src.routers.user import user_router
# from src.routers.post import post_router
# from src.routers.follow import follow_router
# from src.routers.like import like_router
# from src.routers.comment import comment_router


# app = FastAPI()


# app.include_router(user_router)
# app.include_router(post_router)
# app.include_router(follow_router)
# app.include_router(like_router)
# app.include_router(comment_router)


if __name__ == "__main__":
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)
