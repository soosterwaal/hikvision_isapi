TYPED_SUFFIX_PARAMS = [
    {"suffix": "/Color/brightnessLevel", "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Brightness"},
    {"suffix": "/Color/contrastLevel",   "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Contrast"},
    {"suffix": "/Color/saturationLevel", "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Saturation"},
    {"suffix": "/Sharpness/SharpnessLevel",  "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Sharpness"},
    {"suffix": "/Gain/GainLevel", "platform": "number", "min": 0, "max": 100, "step": 1, "name": "Gain"},

    {"suffix": "/ImageFlip/enabled", "platform": "switch", "name": "Image Flip", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/WDR/enabled", "platform": "switch", "name": "WDR", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    #{"suffix": "/BLC/enabled", "platform": "switch", "name": "Backlight Compensation", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/HLC/enabled", "platform": "switch", "name": "Highlight Compensation", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},
    {"suffix": "/DNR/enabled", "platform": "switch", "name": "Digital Noise Reduction", "on": ["true","1","on","enabled"], "off": ["false","0","off","disabled"]},

    {"suffix": "/Shutter/ShutterLevel", "platform": "select", "name": "Shutter Level", "options": ["1/12","1/25","1/50","1/60","1/100","1/120","1/250","1/500","1/1000"]},
    {"suffix": "/WhiteBalance/WhiteBalanceStyle", "platform": "select", "name": "White Balance Style", "options": ["auto1","manual","incandescent","fluorescent","warmLight","natural","streetLamp"]},

]
