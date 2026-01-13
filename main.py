import machine
import utime
import json
import sys
import uselect

# --- 配置区 ---
PWM_PIN = 15
TACHO_PIN = 14
FAN_FREQ = 25000

# --- 全局变量 ---
pulse_count = 0
current_rpm = 0
target_duty_percent = 60  # 初始转速

# --- 初始化硬件 ---
fan_control = machine.PWM(machine.Pin(PWM_PIN))
fan_control.freq(FAN_FREQ)

tacho_input = machine.Pin(TACHO_PIN, machine.Pin.IN, machine.Pin.PULL_UP)


# --- 中断：脉冲计数 ---
def tacho_callback(pin):
    global pulse_count
    pulse_count += 1


tacho_input.irq(handler=tacho_callback, trigger=machine.Pin.IRQ_RISING)


# --- 定时器回调：每秒计算一次 RPM 并上报 ---
def calculate_rpm_callback(timer):
    global pulse_count, current_rpm
    # 计算 RPM (假设每转 2 个脉冲)
    current_rpm = (pulse_count * 60) // 2
    pulse_count = 0  # 重置计数器

    # 构造并打印数据给 Go 程序
    data = {
        "rpm": current_rpm,
        "duty": target_duty_percent
    }
    print(json.dumps(data))


# 注册硬件定时器 (ID=-1 是虚拟定时器，或者用 0)
# period=1000 表示 1000ms 执行一次
timer = machine.Timer(-1)
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=calculate_rpm_callback)

# --- 串口处理逻辑 ---
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)


def update_fan_speed(percentage):
    global target_duty_percent
    target_duty_percent = max(0, min(100, percentage))  # 边界检查
    duty_u16 = int(target_duty_percent * 65535 / 100)
    fan_control.duty_u16(duty_u16)


# --- 主循环：现在只负责处理串口 ---
# 它不再被 sleep(1) 阻塞，响应速度是微秒级的
update_fan_speed(target_duty_percent)  # 执行初始转速

# print("Pico Fan Controller Ready...")

while True:
    if spoll.poll(0):  # 瞬间检查是否有数据
        line = sys.stdin.readline().strip()
        try:
            cmd = json.loads(line)
            if "set_duty" in cmd:
                update_fan_speed(cmd["set_duty"])
        except Exception as e:
            # 可以通过串口发回错误，方便 Go 程序调试
            print(json.dumps({"error": str(e)}))
            pass

    # 这里可以放其他超低延迟的任务，或者直接 pass
    # 建议加一个极小的 sleep 降低功耗
    utime.sleep_ms(10)