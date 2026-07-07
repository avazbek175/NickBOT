class NickForgeError(Exception):
    pass


class UserNotFoundError(NickForgeError):
    pass


class UserBannedError(NickForgeError):
    pass


class ForceJoinRequiredError(NickForgeError):
    pass


class MaintenanceModeError(NickForgeError):
    pass


class InvalidNicknameError(NickForgeError):
    pass


class BroadcastError(NickForgeError):
    pass
