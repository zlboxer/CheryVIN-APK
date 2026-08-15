from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

try:
    from vin_algo import vin_to_pin
except ImportError:
    def vin_to_pin(v):
        return "算法模块未加载"

class Root(BoxLayout):
    def __init__(self):
        super().__init__(orientation='vertical', padding=30, spacing=15)
        self.inp = TextInput(hint_text='输入17位VIN车架号', multiline=False,
                             font_size=18, halign='center')
        self.add_widget(self.inp)
        btn = Button(text='计算 PIN 码', font_size=18, size_hint=(1, 0.4))
        btn.bind(on_press=self.go)
        self.add_widget(btn)
        self.out = Label(text='等待输入', font_size=28, color=(1, 0.7, 0, 1))
        self.add_widget(self.out)

    def go(self, *_):
        try:
            self.out.text = vin_to_pin(self.inp.text)
        except Exception as e:
            self.out.text = str(e)

class VinApp(App):
    def build(self):
        return Root()

if __name__ == '__main__':
    VinApp().run()
