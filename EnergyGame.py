from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from math import sin
from kivy.garden.graph import Graph, MeshLinePlot
import json
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


class Appliance(Widget):
    def __init__(self, typ, icon, rating):
        self.type = typ
        self.icon = icon
        self.rating = rating


class WelcomeScreen(Screen):
    layout = FloatLayout()

    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        background = Image(source="images/background2.png")
        self.layout.add_widget(background)
        welcome_label = Label(text="Energy Game",
                            font_size='24dp',
                            pos_hint={'x': .4, 'y': .7},
                            size_hint=(.2, .1))
        self.layout.add_widget(welcome_label)
        with open('levels.json') as data_file:
            levels = json.load(data_file)
            for i, level in enumerate(levels):
                level_button = Button(text=level["name"],
                              font_size='18dp',
                              pos_hint={'x': .375, 'y': 0.55 - (i * 0.076)},
                              size_hint=(.25, .075))
                level_button.bind(on_press=self.changer)
                self.layout.add_widget(level_button)

        self.add_widget(self.layout)

    def changer(self, *args):
        self.manager.current = 'game_screen'


class GameScreen(Screen):
    level = None
    plot = None
    appliances = []
    locations = [(-0.15, -0.15), (-0.03, -0.15), (0.1, -0.15), (0.2, -0.15)]
    layout = FloatLayout()

    def update(self, dt):
        self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]

    def __init__(self, level, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        with open('levels.json') as data_file:
            levels = json.load(data_file)
            self.level = levels[level]
            for appliance in self.level['appliances']:
                self.appliances.append(Appliance(appliance['type'], appliance['icon'], appliance['rating']))

        background = Image(source="images/background2.png")
        clinic = Image(source="images/clinic.png", pos_hint={'x': .15, 'y': -0.05}, size_hint=(.7, .7))
        sun = Image(source="images/sun.png", pos_hint={'x': .15, 'y': 0.3}, size_hint=(.7, .7))
        self.layout.add_widget(background)
        self.layout.add_widget(clinic)
        self.layout.add_widget(sun)
        for appliance, location in zip(self.appliances, self.locations):
            this_appliance = Image(source=appliance.icon, pos_hint={'x': location[0], 'y': location[1]}, size_hint=(.7, .7))
            self.layout.add_widget(this_appliance)

        graph = Graph(x_ticks_minor=5,
                      x_ticks_major=25, y_ticks_major=1,
                      y_grid_label=True, x_grid_label=True, padding=5,
                      x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=-1, ymax=1,
                      pos_hint={'x': .7, 'y': .7}, size_hint=(.3, .3))
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        graph.add_plot(self.plot)
        self.layout.add_widget(graph)
        self.add_widget(self.layout)


class EnergyGameApp(App):
    def build(self):
        my_screenmanager = ScreenManager()
        welcome_screen = WelcomeScreen(name='welcome_screen')
        game_screen = GameScreen(0, name='game_screen')
        my_screenmanager.add_widget(welcome_screen)
        my_screenmanager.add_widget(game_screen)
        return my_screenmanager

    def set_state(self, state):
        if state == 'main_game':
            self.root.current = 'main_game'
            game = self.root.energy_game
            game.initialise(0)
            Clock.schedule_interval(game.update, 1.0 / 60.0)

if __name__ == "__main__":
    EnergyGameApp().run()
