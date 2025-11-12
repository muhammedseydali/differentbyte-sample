import os
import uuid
import shutil
import schemas
import tempfile

from models import New_Post
from images import imagekit
from sqlalchemy import select
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserRead, UserCreate, UserUpdate
from database import create_db_and_tables, get_async_session
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from fastapi import FastAPI, Depends, File, UploadFile, Form,HTTPException, Path 

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Contact Form API")

# app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
# app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
# app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
# app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
# app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


@app.get("/get_post/")
async def get_new_post(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(New_Post).order_by(New_Post.name.desc()))
    new_posts = result.scalars().all()

    post_data = [
        {
            "id": str(post.id),
            "name": post.name,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name
        }
        for post in new_posts
    ]
    return {"posts": post_data}


@app.post("/new-form")
async def create_new_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    tempfile_path = None

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            tempfile_path = tmp.name
            shutil.copyfileobj(file.file, tmp)

        try:
            upload_result = imagekit.upload_file(
                file=open(tempfile_path, "rb"),
                file_name=file.filename,
                options=UploadFileRequestOptions(
                    use_unique_file_name=True,
                    tags=["backend-upload"]
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ImageKit upload failed: {str(e)}")

        # Ensure upload_result has a URL
        if not upload_result or not hasattr(upload_result, "url"):
            raise HTTPException(status_code=500, detail="ImageKit upload did not return a valid URL")

        # Create DB entry
        new_post = New_Post(
            name=name,
            email=email,
            url=upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "photo",
            file_name=file.filename
        )

        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)

        return {"message": "File uploaded successfully", "data": new_post}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary file
        if tempfile_path and os.path.exists(tempfile_path):
            os.remove(tempfile_path)
        file.file.close()



@app.delete("/post/{post_id}")
async def delete_post(
    post_id: str = Path(..., description="UUID of the post to delete"),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.get(New_Post, post_uuid)
        if not result:
            raise HTTPException(status_code=404, detail="Post not found")

        # Optional: Delete from ImageKit if you store file_id
        # imagekit.delete_file(file_id=result.file_id)

        # Delete from DB
        await session.delete(result)
        await session.commit()

        return {"message": f"Post {post_id} deleted successfully"}

    except ValueError:
        # Raised if the string is not a valid UUID
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))