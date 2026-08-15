from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from vin_core import vin_to_pin

Window.softinput_mode = "below_target"

class CheryVINApp(App):
    def build(self):
        self.root = BoxLayout(orientation="vertical", padding=30, spacing=20)
        self.root.add_widget(Label(text="奇瑞 VIN -> PIN", font_size=26, size_hint=(1,0.15)))
        self.vin = TextInput(hint_text="17位VIN", multiline=False, font_size=22, size_hint=(1,0.2))
        self.root.add_widget(self.vin)
        btn = Button(text="计算", font_size=24, size_hint=(1,0.2))
        btn.bind(on_press=self.calc)
        self.root.add_widget(btn)
        self.out = Label(text="", font_size=24, size_hint=(1,0.25))
        self.root.add_widget(self.out)
        return self.root

    def calc(self, *_):
        try:
            self.out.text = "PIN: " + vin_to_pin(self.vin.text.strip().upper())
        except Exception as e:
            self.out.text = "ERR: " + str(e)

if __name__ == "__main__":
    CheryVINApp().run()
