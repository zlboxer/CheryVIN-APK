"""
CheryVIN - 奇瑞 VIN→PIN 计算工具 (Kivy UI)
核心算法位于 vinpin_core.so (Nuitka 编译，无 Python 源码)
"""
import os, sys

# 确保 .so 可被 import
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# 导入编译后的核心模块
import vinpin_core


class CheryVINApp(App):
    def build(self):
        self.title = "CheryVIN - VIN转PIN"
        root = BoxLayout(orientation="vertical", padding=24, spacing=16)

        # 标题
        title = Label(
            text="[b]奇瑞 VIN → PIN 计算工具[/b]",
            markup=True,
            size_hint_y=None, height=50,
            font_size="22sp",
            color=get_color_from_hex("#1a73e8"),
        )
        root.add_widget(title)

        # 说明
        hint = Label(
            text="请输入17位VIN码（字母自动转大写）",
            size_hint_y=None, height=30,
            font_size="14sp",
            color=get_color_from_hex("#666666"),
        )
        root.add_widget(hint)

        # 输入框
        self.vin_input = TextInput(
            hint_text="例如: LFV2A11B0G3045678",
            multiline=False,
            size_hint_y=None, height=50,
            font_size="18sp",
            input_filter="str",
            padding=[12, 12, 12, 12],
        )
        self.vin_input.bind(text=self._on_vin_text)
        root.add_widget(self.vin_input)

        # 计算按钮
        self.calc_btn = Button(
            text="🔐 计算 PIN 码",
            size_hint_y=None, height=55,
            font_size="18sp",
            background_color=get_color_from_hex("#1a73e8"),
            color=(1, 1, 1, 1),
        )
        self.calc_btn.bind(on_press=self._calc_pin)
        root.add_widget(self.calc_btn)

        # 结果区域
        self.result_label = Label(
            text="",
            size_hint_y=None, height=80,
            font_size="20sp",
            markup=True,
            halign="center",
            valign="middle",
        )
        root.add_widget(self.result_label)

        # 历史记录
        hist_title = Label(
            text="[b]历史记录[/b]",
            markup=True,
            size_hint_y=None, height=35,
            font_size="16sp",
            color=get_color_from_hex("#444444"),
        )
        root.add_widget(hist_title)

        scroll = ScrollView(size_hint=(1, 1))
        self.history_label = Label(
            text="",
            size_hint_y=None,
            font_size="14sp",
            markup=True,
            halign="left",
            valign="top",
            text_size=(400, None),
        )
        self.history_label.bind(texture_size=self._update_history_height)
        scroll.add_widget(self.history_label)
        root.add_widget(scroll)

        self.history = []
        return root

    def _on_vin_text(self, instance, value):
        # 自动转大写 + 限制17位
        upper = value.upper()
        upper = "".join(c for c in upper if c.isalnum())[:17]
        if upper != value:
            instance.text = upper

    def _calc_pin(self, instance):
        vin = self.vin_input.text.strip()
        if len(vin) != 17:
            self.result_label.text = "[color=#d32f2f]❌ VIN 必须是17位[/color]"
            return
        try:
            pin = vinpin_core.vin_to_pin(vin)
            self.result_label.text = (
                f"[color=#1b5e20]✅ PIN 码: [b]{pin}[/b][/color]"
            )
            self.history.insert(0, f"[color=#333]{vin}[/color] → [b]{pin}[/b]")
            self.history_label.text = "\n".join(self.history[:20])
        except Exception as e:
            self.result_label.text = f"[color=#d32f2f]❌ {e}[/color]"

    def _update_history_height(self, instance, size):
        instance.height = max(size[1], 40)


if __name__ == "__main__":
    CheryVINApp().run()
