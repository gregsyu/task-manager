class ErrorMsg:
    TASK_NOT_FOUND          = "Task not found"
    TASK_FORBIDDEN          = "Access denied - user doesn't own task"
    INVALID_STATUS          = "Invalid status value"
    INVALID_PRIORITY        = "Invalid priority value"
    TASK_CREATE_FAILED      = "Failed to create task"
    USER_NOT_FOUND          = "User not found"
    INVALID_CREDENTIALS     = "Invalid credentials"
    TOKEN_EXPIRED           = "Token has expired"
    INTERNAL_SERVER_ERROR   = "Internal server error"
    UNAUTHORIZED            = "Not Authorized"


class SuccessMsg:
    TASK_CREATED            = "Task created successfully"
    TASK_UPDATED            = "Task updated successfully"
    TASK_DELETED            = "Task deleted successfully"
    SUCCESSFUL_LOGIN        = "Successful login"
    USER_REGISTERED         = "User registered"