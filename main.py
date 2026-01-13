import machine
import utime
import json
import sys
import uselect

# --- 配置区 ---
PWM_PIN = 15
TACHO_PIN = 14
FAN_FREQ = 25000  # 标准 PWM 风扇频率 25kHz

# --- 初始化 ---
# PWM 设定
fan_control = machine.PWM(machine.Pin(PWM_PIN))
fan_control.freq(FAN_FREQ)

# Tacho 设定（使用内部上拉电阻，省去额外硬件）
tacho_input = machine.Pin(TACHO_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

pulse_count = 0


def tacho_callback(pin):
    global pulse_count
    pulse_count += 1


# 绑定中断：上升沿触发
tacho_input.irq(handler=tacho_callback, trigger=machine.Pin.IRQ_RISING)

# --- 串口非阻塞监听初始化 ---
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

def check_usb_input():
    """检查是否有来自电脑的指令"""
    if spoll.poll(0): # 非阻塞检查
        line = sys.stdin.readline().strip()
        try:
            # 假设电脑发送的是 {"set_duty": 80}
            cmd = json.loads(line)
            if "set_duty" in cmd:
                new_duty = int(cmd["set_duty"] * 65535 / 100)
                fan_control.duty_u16(new_duty)
        except:
            pass # 忽略格式错误的指令



# --- 主逻辑 ---
def set_fan_speed(percentage):
    """设置风扇速度 0-100"""
    # 将 0-100 映射到 0-65535 (16位占空比)
    duty = int(percentage * 65535 / 100)
    fan_control.duty_u16(duty)


try:
    while True:
        # 1. 设定转速（比如 60%）
        set_fan_speed(60)

        # 2. 采样 1 秒来计算 RPM
        pulse_count = 0
        utime.sleep(1)

        # 计算 RPM (假设每转 2 个脉冲)
        rpm = (pulse_count * 60) // 2
        data = {"rpm": rpm, "duty": 60}
        print(json.dumps(data))
        # print(f"Target: 60% | Current Speed: {rpm} RPM")

except KeyboardInterrupt:
    # 优雅退出：停止风扇
    fan_control.duty_u16(0)
    print("Program stopped")