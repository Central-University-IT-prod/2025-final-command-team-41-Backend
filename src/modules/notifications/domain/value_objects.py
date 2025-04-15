from enum import Enum


class DeviceType(str, Enum):
    ANDROID = 'android'
    IOS = 'ios'
    WEB = 'web'
