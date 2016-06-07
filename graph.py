from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.app import App

from random import gauss

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

GridLayout:
    cols: 2
    Graph:
        max: 100
        values: app.values

    Button:
        text: 'push me'
        size_hint_x: None
        on_press:
            Animation(
            values=[gauss(50, 10) for x in enumerate(app.values)],
            t='out_quad').start(app)

    Graph:
        max: 1
        values: app.running_values

    ToggleButton:
        text: 'push me'
        size_hint_x: None
        on_state:
            if self.state == 'down': Clock.schedule_interval(app.add_running_values, 0)
            else: Clock.unschedule(app.add_running_values)

'''  # noqa


class Graph(App):
    values = ListProperty([x for x in range(100)])
    running_values = ListProperty([])

    def build(self):
        return Builder.load_string(KV)

    def add_running_values(self, dt):
        self.running_values.append(gauss(.5, .1))
        self.running_values = self.running_values[-100:]

if __name__ == '__main__':
    Graph().run()