#!/usr/bin/env python3
"""
CheryVIN - Kivy UI 薄壳
核心算法在 vinpin_core.so 中（无源码）
"""
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

# 从编译后的 .so 导入核心函数
try:
    from vinpin_core import vin_to_pin
    CORE_OK = True
except Exception as e:
    CORE_OK = False
    CORE_ERR = str(e)

class CheryVINApp(App):
    def build(self):
        self.title = "CheryVIN - VIN转PIN"
        root = BoxLayout(orientation="vertical", padding=20, spacing=15)

        # 标题
        root.add_widget(Label(
            text="奇瑞 VIN → PIN 计算工具",
            font_size="22sp", bold=True,
            size_hint_y=None, height=50
        ))

        # 说明
        root.add_widget(Label(
            text="请输入17位VIN码",
            font_size="14sp",
            size_hint_y=None, height=30
        ))

        # 输入框
        self.vin_input = TextInput(
            hint_text="如 LSJCRF3H0HX000001",
            multiline=False,
            font_size="18sp",
            size_hint_y=None, height=50,
            input_filter="uppercase",
            max_text_length=17
        )
        root.add_widget(self.vin_input)

        # 计算按钮
        self.btn = Button(
            text="🔐 计算 PIN 码",
            font_size="18sp",
            size_hint_y=None, height=55,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        self.btn.bind(on_press=self.on_calc)
        root.add_widget(self.btn)

        # 结果区域
        self.result_label = Label(
            text="",
            font_size="20sp",
            color=(0, 0.8, 0, 1),
            size_hint_y=None, height=60,
            markup=True
        )
        root.add_widget(self.result_label)

        # 错误区域
        self.error_label = Label(
            text="",
            font_size="14sp",
            color=(1, 0, 0, 1),
            size_hint_y=None, height=80,
            markup=True
        )
        root.add_widget(self.error_label)

        # 历史记录
        root.add_widget(Label(
            text="── 历史记录 ──",
            font_size="14sp",
            size_hint_y=None, height=30
        ))

        self.history = Label(
            text="(暂无)",
            font_size="13sp",
            size_hint_y=None,
            halign="left", valign="top"
        )
        self.history.bind(texture_size=self._update_height)
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.history)
        root.add_widget(scroll)

        self.history_list = []

        if not CORE_OK:
            self.error_label.text = f"[red]核心模块加载失败: {CORE_ERR}[/red]"

        return root

    def _update_height(self, instance, size):
        instance.height = max(size[1], 40)

    def on_calc(self, *args):
        self.error_label.text = ""
        self.result_label.text = ""

        vin = self.vin_input.text.strip().upper()
        if len(vin) != 17:
            self.error_label.text = f"[red]❌ VIN必须为17位，当前{len(vin)}位[/red]"
            return

        try:
            pin = vin_to_pin(vin)
            self.result_label.text = f"[b]PIN 码: {pin}[/b]"
            self.history_list.insert(0, f"{vin} → {pin}")
            self.history.text = "\n".join(self.history_list[:20])
            self.vin_input.text = ""
        except Exception as e:
            err_msg = str(e)[:100]
            self.error_label.text = f"[red]❌ {err_msg}[/red]"

if __name__ == "__main__":
    CheryVINApp().run()
