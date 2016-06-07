from kivy.core.window import Window
Window.size = (850, 400)
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.app import App

from random import gauss
from kivy.clock import Clock

KV = '''
#:import Animation kivy.animation.Animation
#:import chain itertools.chain
#:import gauss random.gauss
#:import Clock kivy.clock.Clock

<Graph@Widget>:
    max: 100
    values: []
    canvas:
        Line:
            points:
                list(chain(*
                [[
                self.x + x * self.width / len(self.values),
                self.y + y * self.height / self.max
                ] for x, y in enumerate(self.values)])) if self.values else []

FloatLayout:
    Image:
        pos_hint: {"x": 0, 'y':0}
        source: 'images/background2.png'
    Image:
        pos_hint: {"x": 0, 'y':0}
        source: 'images/cloud.png'
    Graph:
        pos_hint: {"x": 0.7, 'y':0.8}
        size_hint: 0.3, 0.2
        max: 1
        values: app.running_values


'''  # noqa


class Graph(App):
    values = ListProperty([x for x in range(100)])
    running_values = ListProperty([])

    def build(self):
        Clock.schedule_interval(self.add_running_values, 0)
        return Builder.load_string(KV)

    def add_running_values(self, dt):
        self.running_values.append(gauss(.5, .1))
        self.running_values = self.running_values[-100:]

if __name__ == '__main__':
    Graph().run()