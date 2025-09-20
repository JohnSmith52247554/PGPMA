'''
class Msg:
    CREATE_ERROR_WINDOW = "__CREATE__ERROR__WINDOW__"

    OPEN_PORT = "__OPEN__PORT__"
    OPEN_PORT_FAILED = "__OPEN__PORT__FAILED"
    OPEN_PORT_OK = "__OPEN__PORT__OK"

    SET_PROGRESS_BAR = "__SET__PROGRESS__BAR__"

    RESET = "__RESET__"
    STOP = "__STOP__"
    OPEN_GRIPPER = "__OPEN__GRIPPER__"
    CLOSE_GRIPPER = "__CLOSE__GRIPPER__"

    SEND_ORTHOGONAL_CMD = "__SEND__ORTHOGONAL__CMD__"
    SEND_JOINT_CMD = "__SEND__JOINT__CMD__"

    READ_STATE = "__READ__STATE__"
'''

class MsgType:
    CREATE_ERROR_WINDOW = 0
    CREATE_INFO_WINDOW = 1

    ENABLE_PORT_MONITOR = 2
    DISABLE_PORT_MONITOR = 3

    OPEN_PORT = 10

    SET_PROGRESS_BAR = 20

    RESET = 30
    STOP = 31
    OPEN_GRIPPER = 32
    CLOSE_GRIPPER = 33

    SEND_ORTHOGONAL_CMD = 40
    SEND_JOINT_CMD = 41
    SEND_SET_SPEED_CMD = 42

    READ_STATE = 50

    SET_IMM_CONSOLE_TEXT = 60

    WRITE_FLASH = 70
    READ_FLASH = 71
    CLEAN_FLASH = 72

    VISUAL_MODE = 80


class Message:
    def __init__(self, msg_type : MsgType, data = None):
        self.dict = {
            "type" : msg_type,
            "data" : data
        }