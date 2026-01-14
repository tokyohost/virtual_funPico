import json
import machine
import utime
import sys
import uselect

# --- 配置部分 ---
fans = {
    "fan1": {
        "PWM_PIN":15,
        "FAN_FREQ":14,
        "pwm": machine.PWM(machine.Pin(15)),
        "tach": machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP),
        "pulses": 0,
        "missing_cycles": 0  # 新增：连续未检测到转速的周期数
    },
    "fan2": {
        "PWM_PIN":13,
        "FAN_FREQ":12,
        "pwm": machine.PWM(machine.Pin(13)),
        "tach": machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP),
        "pulses": 0,
        "missing_cycles": 0  # 新增：连续未检测到转速的周期数
    }
}


# 初始化 PWM 频率和中断
def create_callback(fan_name):
    def callback(pin):
        fans[fan_name]["pulses"] += 1

    return callback


for name, config in fans.items():
    config["pwm"].freq(25000)
    config["pwm"].duty_u16(100)  # 初始停止
    config["tach"].irq(trigger=machine.Pin.IRQ_FALLING, handler=create_callback(name))


# --- 定时器：每秒上报一次数据 ---
def calculate_rpm_callback(timer):
    report_list = []

    for name, config in fans.items():
        p = config["pulses"]
        rpm = (p * 60) // 2
        duty_u16 = config["pwm"].duty_u16()
        duty_pct = int(duty_u16 * 100 / 65535)

        # --- 判断逻辑开始 ---
        # 如果设置了占空比，但 RPM 是 0
        if duty_u16 > 0 and rpm == 0:
            config["missing_cycles"] += 1
        else:
            config["missing_cycles"] = 0

        # 判定标准：如果连续 3 秒（3个周期）都是 0 转速，且 PWM > 0，则认为没接
        # 或者 PWM 本身就是 0，我们也可以选择不上报（看你的需求）
        is_present = True
        if (duty_u16 > 0 and config["missing_cycles"] >= 10) or (duty_u16 == 0 and rpm == 0):
            is_present = False
        # --- 判断逻辑结束 ---

        # 只有判定为“在场”的风扇才加入列表
        if is_present:
            report_list.append({
                "id": name,
                "rpm": rpm,
                "duty": duty_pct
            })

        config["pulses"] = 0

    # 如果列表不为空（至少有一个风扇接了），才打印上报
    if len(report_list) > 0:
        print(json.dumps({"fans": report_list}))
    else:
        pass # 保持沉默，不上报


# 启动定时器 (每 1000 毫秒执行一次)
timer = machine.Timer(-1)
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=calculate_rpm_callback)

# --- 主循环：非阻塞读取串口指令 ---
spoll = uselect.poll()
spoll.register(sys.stdin, uselect.POLLIN)

print("Pico Fan Controller Ready...")

while True:
    # 检查是否有串口输入
    if spoll.poll(0):
        line = sys.stdin.readline().strip()
        try:
            data = json.loads(line)
            target_fan = data.get("fan")
            duty = data.get("set_duty")
            if target_fan in fans and duty is not None:
                # 限制 duty 范围 0-100
                duty = max(0, min(100, duty))
                fans[target_fan]["pwm"].duty_u16(int(duty * 65535 / 100))
        except Exception as e:
            # 解析失败时不崩溃，保持运行
            pass

    utime.sleep_ms(10)  # 稍微休息，降低 CPU 占用