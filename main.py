from machine import Pin, SoftI2C, Timer
import time
import ssd1306
import micropython
from array import array



# OLED reset pin
i2c_rst = Pin(16, Pin.OUT)
# Initialize the OLED display
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1) # must be held high after initialization
# Create the bus object
i2c = SoftI2C(scl=Pin(15, Pin.OUT, Pin.PULL_UP), 
              sda=Pin(4, Pin.OUT, Pin.PULL_UP))
# Create the display object
oled = ssd1306.SSD1306_I2C(128, 64, i2c)


class ControlBoards():
    def __init__(self, button_pins : list, options : list):
        self.button = button_pins

        # Variables for buttons check
        self.button_prev_state = array('b', [False, False, False])
        self.button_press_counter = array('I', [0, 0, 0])
        self.same_long = array('b', [False, False, False])

        # Timers
        self.tim = Timer(4)
        self.tim.init(period=50, mode=Timer.PERIODIC, callback=self.check_buttons)

        # Handle allocations (can't be allocated in ISR or callback)
        self.handle_long_press_ref = [self.handle_long_press_selection, self.handle_long_press_right, self.handle_long_press_left]
        self.handle_short_press_ref = [self.handle_short_press_selection, self.handle_short_press_right, self.handle_short_press_left]

        # State variables
        self.editing_mode = False
        self.current_selection = 0
        self.selection_list = options

    def handle_long_press_selection(self, _):
        print("Editing mode")
        oled.fill(0)
        oled.text("Editing mode", 0, 0)
        oled.show()
        
    def handle_short_press_selection(self, setting_mode=False):
        if setting_mode:
            self.current_selection = (self.current_selection) % len(self.selection_list)
        else:
            self.current_selection = (self.current_selection + 1) % len(self.selection_list)    
        print(self.selection_list[self.current_selection])
        oled.fill(0)
        oled.text(self.selection_list[self.current_selection], 0, 0)
        oled.show()
    
    def handle_long_press_right(self, _):
        print("right ++")
        oled.fill(0)
        oled.text("right ++", 0, 0)
        oled.show()
        
    def handle_short_press_right(self, _):
        print("right +")
        oled.fill(0)
        oled.text("right +", 0, 0)
        oled.show()

    def handle_long_press_left(self, _):
        print("left ++")
        oled.fill(0)
        oled.text("left ++", 0, 0)
        oled.show()
        
    def handle_short_press_left(self, _):
        print("left +")
        oled.fill(0)
        oled.text("left +", 0, 0)
        oled.show()

    def check_buttons(self, t):
        # ISR called by self.tim every period
        for button_idx in range(3):
            if button_idx != 0 and not self.editing_mode:
                break
            state = self.button[button_idx].value()
            if state == False and self.button_prev_state[button_idx] == True :
                if self.button_press_counter[button_idx] <= 10:
                    if button_idx == 0 and self.editing_mode:
                        self.editing_mode = False
                        micropython.schedule(self.handle_short_press_ref[button_idx], True)
                    else:
                        micropython.schedule(self.handle_short_press_ref[button_idx], 0)
                    
                self.button_press_counter[button_idx] = 0
                self.same_long[button_idx] = False
            elif state == True and self.button_prev_state[button_idx] == True:
                self.button_press_counter[button_idx] += 1

            if self.button_press_counter[button_idx] > 10 and self.same_long[button_idx] == False:
                micropython.schedule(self.handle_long_press_ref[button_idx], 0)
                self.same_long[button_idx] = True
                if button_idx == 0:
                    self.editing_mode = True

            self.button_prev_state[button_idx] = state
        
    def stop_timer(self):
        self.tim.deinit()

def test3():

    
    my_pins = [Pin(36, Pin.IN), 
               Pin(38, Pin.IN), 
               Pin(37, Pin.IN)]
    my_options = ["Opt1", "Opt2", "Opt3"]

    print(my_options[0])
    oled.fill(0)
    oled.text(my_options[0], 0, 0)
    oled.show()

    my_control_board = ControlBoards(button_pins=my_pins, options=my_options)
    time.sleep(20)
    my_control_board.stop_timer()

    oled.fill(0)
    oled.show()