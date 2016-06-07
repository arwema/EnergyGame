from kivy.app import App

from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from math import sin
from kivy.garden.graph import Graph, MeshLinePlot
import json
from kivy.clock import Clock
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


class Appliance(Widget):
    def __init__(self, typ, icon, rating):
        self.type = typ
        self.icon = icon
        self.rating = rating


class WelcomeScreen(FloatLayout):
    pass


class EnergyGame(FloatLayout):
    level = None
    plot = None
    appliances = []
    locations = [(-0.15, -0.15), (-0.03, -0.15), (0.1, -0.15), (0.2, -0.15)]

    def update(self, dt):
        self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]

    def initialise(self, level):
        with open('levels.json') as data_file:
            levels = json.load(data_file)
            self.level = levels[level]
            for appliance in self.level['appliances']:
                self.appliances.append(Appliance(appliance['type'], appliance['icon'], appliance['rating']))

        background = Image(source="images/background2.png")
        clinic = Image(source="images/clinic.png", pos_hint={'x': .15, 'y': -0.05}, size_hint=(.7, .7))
        sun = Image(source="images/sun.png", pos_hint={'x': .15, 'y': 0.3}, size_hint=(.7, .7))
        self.add_widget(background)
        self.add_widget(clinic)
        self.add_widget(sun)
        for appliance, location in zip(self.appliances, self.locations):
            this_appliance = Image(source=appliance.icon, pos_hint={'x': location[0], 'y': location[1]}, size_hint=(.7, .7))
            self.add_widget(this_appliance)

        graph = Graph(x_ticks_minor=5,
                      x_ticks_major=25, y_ticks_major=1,
                      y_grid_label=True, x_grid_label=True, padding=5,
                      x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=-1, ymax=1,
                      pos_hint={'x': .7, 'y': .7}, size_hint=(.3, .3))
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        graph.add_plot(self.plot)
        self.add_widget(graph)


class EnergyGameApp(App):
    def build(self):
        pass

    def set_state(self, state):
        if state == 'main_game':
            self.root.current = 'main_game'
            game = self.root.energy_game
            game.initialise(0)
            Clock.schedule_interval(game.update, 1.0 / 60.0)

if __name__ == "__main__":
    EnergyGameApp().run()
