# virtual_funPico

## 项目简介

`virtual_funPico` 是一个运行在 Raspberry Pi Pico（RP2040）上的固件项目。  
它通过 USB（CDC/串口）接收风扇转速指令，并输出 PWM 信号控制物理风扇。

该项目与以下组件配合使用：
- `virtual_fun_kernel`（Linux 虚拟风扇内核驱动） https://github.com/tokyohost/virtual_fun_kernel
- `virtualFunGo`（Go 语言桥接服务） https://github.com/tokyohost/virtualFunGo

三者组合后，可为不支持风扇调速的主板提供完整解决方案。

---

## 功能特性

- USB CDC / 串口通信
- 简单的文本控制协议
- PWM 风扇调速输出
- 支持 5V / 12V PWM 风扇
- 固件轻量、易扩展

---

## 系统架构

Linux（virtual_fun_kernel）
→ virtualFunGo（Go 桥接）
→ USB 串口
→ Raspberry Pi Pico（virtual_funPico）
→ PWM → 物理风扇

---

## USB 协议示例

```
{"fan":"fan1","set_duty",255}
```

- set_duty 数值范围：0–255
- fan 风扇ID

---

## 构建与烧录

你可以使用GoLand + microPython Tools 插件 Upload Project 至Pico 设备

---

## 许可证

MIT License
