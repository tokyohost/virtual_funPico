# virtual_funPico

## Project Overview

`virtual_funPico` is a firmware project running on the **Raspberry Pi Pico (RP2040)**.  
It receives fan speed commands via USB (CDC/Serial) and outputs PWM signals to control physical fans.

This project works together with the following components:
- `virtual_fun_kernel` (Linux virtual fan kernel driver)  
  https://github.com/tokyohost/virtual_fun_kernel
- `virtualFunGo` (Go-based bridge service)  
  https://github.com/tokyohost/virtualFunGo

When combined, these components provide a complete fan control solution for motherboards that do **not** support native fan speed control.

---

## Features

- USB CDC / Serial communication
- Simple text-based control protocol
- PWM-based fan speed output
- Supports 5V / 12V PWM fans
- Lightweight and easily extensible firmware

---

## System Architecture

Linux (`virtual_fun_kernel`)  
→ `virtualFunGo` (Go bridge)  
→ USB Serial  
→ Raspberry Pi Pico (`virtual_funPico`)  
→ PWM → Physical Fan

---

## USB Protocol Example

```json
{"fan":"fan1","set_duty":255}
