#!/bin/bash
openocd -f interface/stlink-v2.cfg -f target/stm32f4x.cfg -c init -c 'reset halt' -c 'flash write_image erase firmware.elf' -c 'flash verify_image firmware.elf' -c 'reset run' -c exit
