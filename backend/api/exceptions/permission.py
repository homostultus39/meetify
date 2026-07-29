class RolePermissionError(Exception):
    pass

class PermissionDeniedError(RolePermissionError):
    pass