# This file is executed on every boot (including wake-boot from deepsleep)
import esp
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
gc.collect()

import main
