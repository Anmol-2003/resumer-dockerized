from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models.db_models import Users
from utils.db_connector import get_async_session
from models.api_models import SignUp, Login
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os 
from dotenv import load_dotenv
load_dotenv(override=True)

os.environ['SECRET_KEY'] = os.getenv('SECRET_KEY')

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # -- 1 hour 

@router.get('/auth/me')
async def authenticateToken(request : Request): # The request is of type get, the server automatically gets the token from the localStorage
    access_token = request.headers.get('Authorization')
    print(access_token)
    if access_token is None:
        return JSONResponse(content={
            'message' : 'Authentication error - access token is null', 
        }, status_code=401)
    try:
        token = access_token.split(" ")[1] 
        payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=[ALGORITHM])
        userId = payload.get('userId')
        return JSONResponse(content={'message' : 'Authentication successful', 'data' : userId})
    except JWTError as e:
        print('JWTError-', e)
        return JSONResponse(content={'message' : 'Token is expired'}, status_code=500)
    except Exception as e:
        print('Server Exception ', e)
        return JSONResponse(content={'message' : 'Exception occured in the server'}, status_code=500)

@router.post('/auth/signup')
async def signup(userData: SignUp, session: AsyncSession = Depends(get_async_session)):
    hashed_password = pwd_context.hash(userData.password)
    newUser = Users(name = userData.name, email = userData.email, password = hashed_password)
    
    # Using async with session.begin() for automatic rollback and commits
    try:
        async with session.begin():
            print('Inserting new user details')
            session.add(newUser)
        
        await session.commit()
        print('Data inserted')
        async with session.begin():
            res = await session.execute(
                text('SELECT userId FROM users WHERE email = :email'), 
                {'email': userData.email}
            )
            userId = res.scalar_one_or_none()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"userId": userId}, expires_delta=access_token_expires)
        
        print("Access Token: ", access_token)
        response = JSONResponse(content={'message' : 'Account created', 'data' : userId, 'token' : access_token}, status_code=200)
        return response
    except SQLAlchemyError as e:
        print('SQLAlchemy error ', e)
        return JSONResponse(content={'message' : 'SQL error while account creation'}, status_code=500)
    except Exception as e:
        print(e)
        return JSONResponse(content={'message' : 'Error in creating the account'}, status_code=500)

@router.post('/auth/login')
async def login(userData: Login, session: AsyncSession = Depends(get_async_session)):

    try: 
        async with session.begin():
            res = await session.execute(text('select * from users where email = :email'), {'email' : userData.email})
            user = res.mappings().one_or_none()
            print(user)
        # Verifying the user
        if not user or not pwd_context.verify(userData.password, user.password):
            return JSONResponse(content={'message' : 'Invalid Credentials'}, status_code=401)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"userId": user.userId}, expires_delta=access_token_expires)
        print("Access Token: ", access_token)
        response = JSONResponse(content={'message' : 'Login successful', 'data' : user.userId, 'token' : access_token})
        return response
    except Exception as e: 
        print(e)
        return  JSONResponse(content={'message' : 'Error in logging in'}, status_code=500)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if(expires_delta):
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ['SECRET_KEY'], algorithm=ALGORITHM)
    return encoded_jwt