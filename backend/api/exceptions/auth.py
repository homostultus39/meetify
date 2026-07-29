class TokenError(Exception):
    pass

class TokenExpiredError(TokenError):
    pass

class TokenInvalidError(TokenError):
    pass

class RefreshTokenMissing(TokenError):
    pass

class AuthError(Exception):
    pass

class InvalidCredentialsError(AuthError):
    pass