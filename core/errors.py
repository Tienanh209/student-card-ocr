class ServiceError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"


class ImageDecodeError(ServiceError):
    status_code, code = 400, "IMAGE_DECODE_ERROR"


class EmptyFileError(ServiceError):
    status_code, code = 400, "EMPTY_FILE"


class ImageTooLargeError(ServiceError):
    status_code, code = 413, "IMAGE_TOO_LARGE"


class InvalidStudentIdError(ServiceError):
    status_code, code = 422, "INVALID_STUDENT_ID"


class ModelBackendError(ServiceError):
    status_code, code = 503, "MODEL_BACKEND_ERROR"
