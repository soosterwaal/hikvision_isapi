TYPED_SUFFIX_PARAMS = [
    {"suffix": "/Brightness/level", "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Brightness"},
    {"suffix": "/Contrast/level",   "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Contrast"},
    {"suffix": "/Saturation/level", "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Saturation"},
    {"suffix": "/Sharpness/level",  "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Sharpness"},
    {"suffix": "/Exposure/ExposureCompensation", "platform": "number", "min": -5, "max": 5, "step": 1, "name": "Exposure Compensation"},
    {"suffix": "/Gain/level", "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Gain"},

    {"suffix": "/ImageFlip/enabled", "platform": "switch", "name": "Image Flip", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/WDR/enabled", "platform": "switch", "name": "WDR", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/BLC/enabled", "platform": "switch", "name": "Backlight Compensation", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/HLC/enabled", "platform": "switch", "name": "Highlight Compensation", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/DNR/enabled", "platform": "switch", "name": "Digital Noise Reduction", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},

    {"suffix": "/DayNight/DayNightFilterType", "platform": "select", "name": "Day/Night Mode", "options": ["day","night","auto","schedule","alarm"]},
    {"suffix": "/Shutter/ShutterMode", "platform": "select", "name": "Shutter Mode", "options": ["manual","shutterPriority","auto"]},
    {"suffix": "/Shutter/ShutterTime", "platform": "select", "name": "Shutter Time", "options": ["1/12","1/25","1/50","1/60","1/100","1/120","1/250","1/500","1/1000"]},
    {"suffix": "/WhiteBalance/WhiteBalanceMode", "platform": "select", "name": "White Balance Mode", "options": ["auto","manual","incandescent","fluorescent","warmLight","natural","streetLamp"]},
    {"suffix": "/MixedLight/mixedLightBrightnessRegulatMode", "platform": "select", "name": "Mixed Light Mode", "options": ["auto","manual","off"]}
]
