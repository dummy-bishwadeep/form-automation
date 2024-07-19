import os
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, APIKeyCookie

security_header = APIKeyHeader(name="login-token", auto_error=False)
# security_cookie = APIKeyCookie(name="login-token", auto_error=False)


async def verify_cookie(token: str = Depends(security_header)):
    try:
        url = os.getenv("AUTH_ENDPOINT")
        headers = {'login-token': f'{token}'}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Cookie')
            return response.json()
    except Exception as cookie_error:
        raise cookie_error



