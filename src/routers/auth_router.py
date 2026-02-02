from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..schemas.auth import UserCreate, UserOut, Token
from ..database import User
from ..messages import ErrorMsg, SuccessMsg
from sqlalchemy.orm import Session
from ..security import get_password_hash, verify_password, create_access_token
from ..dependencies import get_db, get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"detail": ErrorMsg.UNAUTHORIZED}},
)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": SuccessMsg.USER_REGISTERED},
        400: {"description": "User already exists or invalid data"},
    },
)
def register_user(user_in: UserCreate, db: Annotated[Session, Depends(get_db)]):
    existing_user = (
        db.query(User)
        .filter((User.username == user_in.username) | (User.email == user_in.email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorMsg.USER_ALREADY_EXISTS
        )

    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {"description": SuccessMsg.SUCCESSFUL_LOGIN},
        401: {"description": ErrorMsg.INVALID_CREDENTIALS},
    },
)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ErrorMsg.INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserOut,
)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# @router.put(
#     "/me/password",
#     response_model=UserOut,
#     responses={
#         200: {"description": "Senha alterada com sucesso"},
#         400: {"description": "Senha atual incorreta ou nova senha inválida"},
#     },
# )
# def change_password(
#     password_change: UserPasswordChange, current_user: CurrentUser, db: DB
# ):
#     if not verify_password(
#         password_change.current_password, current_user.hashed_password
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=ErrorMsg.INVALID_CURRENT_PASSWORD,
#         )
#
#     current_user.hashed_password = get_password_hash(password_change.new_password)
#     db.commit()
#     db.refresh(current_user)
#
#     return current_user


def authenticate_user(
    db: Session, username_or_email: str, password: str
) -> User | None:
    user = (
        db.query(User)
        .filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        )
        .first()
    )

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
