CURRENT_CITY = "Seattle"
MOISTURE_DECAY_RATE = 0.05
FERTILIZER_DECAY_RATE = 0.01

def set_moisture_decay_rate(decay_rate):
    if decay_rate < 0:
        raise ValueError("Decay rate cannot be negative")

    global MOISTURE_DECAY_RATE
    MOISTURE_DECAY_RATE = decay_rate