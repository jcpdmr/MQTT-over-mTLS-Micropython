from machine import Pin, SoftI2C, Timer
import time
import ssd1306

button = Pin(36, Pin.IN)
led = Pin(25, Pin.OUT)

# Preparazione display OLED
oled_width = 128
oled_height = 64
# OLED reset pin
i2c_rst = Pin(16, Pin.OUT)
# Initialize the OLED display
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1) # must be held high after initialization
# Setup the I2C lines
i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)
# Create the bus object
i2c = SoftI2C(scl=i2c_scl, sda=i2c_sda)
# Create the display object
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)


def test(): 
    while True:
        state = button.value()
        if state == False:
            oled.fill(0)
        else:
            oled.fill(0)
            oled.text("test", 0, 0)
        time.sleep_ms(200)
        oled.show()


def test2():
    tim0 = Timer(0)
    tim0.init(period=50, mode=Timer.PERIODIC, callback=check_button)
    time.sleep(10)
    tim0.deinit()

button_prev_state = False
button_press_counter = 0

def check_button(t):
    global button_prev_state
    global button_press_counter

    state = button.value()
    if state == False and button_prev_state == True :
        if button_press_counter <= 10:
            oled.fill(0)
            oled.text("single_press", 0, 0)
        button_press_counter = 0
    elif state == True and button_prev_state == True:
        button_press_counter += 1

    if button_press_counter > 10:
        oled.fill(0)
        oled.text("long_press", 0, 0)

    button_prev_state = state
    oled.show()