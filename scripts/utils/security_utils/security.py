import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from scripts.constants.api_constants import BaseURLPaths

security_header = APIKeyHeader(name="login-token", auto_error=False)


async def verify_cookie(token: str = Depends(security_header)):
    try:
        headers = {'login-token': f'{token}'}
        async with httpx.AsyncClient() as client:
            response = await client.get(BaseURLPaths.auth_endpoint, headers=headers)
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Cookie')
            return {'login-token': token}
    except Exception as cookie_error:
        raise cookie_error



