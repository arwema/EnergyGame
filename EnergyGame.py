from kivy.app import App

import kivy
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from math import sin
from kivy.garden.graph import Graph, MeshLinePlot
import json
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


class GameSession:
    levels = []
    level = None
    welcome_screen = None
    game_screen = None

    def __init__(self):
        pass

    def add_level(self, level):
        self.levels.append(level)

    def set_level(self, level):
        self.level = level

    def set_welcome_screen(self, welcome_screen):
        self.welcome_screen = welcome_screen

    def set_game_screen(self, game_screen):
        self.game_screen = game_screen


class Level:
    appliances = []
    name = None

    def __init__(self, name):
        self.name = name

    def add_appliance(self, appliance):
        self.appliances.append(appliance)


class Appliance(ToggleButtonBehavior, Image):
    def __init__(self, typ, icon, rating, **kwargs):
        super(Appliance, self).__init__(**kwargs)
        self.type = typ
        self.icon = icon
        self.rating = rating
        self.source = icon

    def on_state(self, widget, value):
        if value == 'down':
            self.source = self.icon
        else:
            self.source = "images/off.png"


class WelcomeScreen(Screen):
    layout = FloatLayout()

    def __init__(self, game_session, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.game_session = game_session
        background = Image(source="images/background2.png")
        self.layout.add_widget(background)
        welcome_label = Label(text="Energy Game",
                            font_size='24dp',
                            pos_hint={'x': .4, 'y': .7},
                            size_hint=(.2, .1))
        self.layout.add_widget(welcome_label)
        for i, level in enumerate(self.game_session.levels):
            level_button = Button(text=level.name,
                          font_size='18dp',
                          pos_hint={'x': .375, 'y': 0.55 - (i * 0.076)},
                          size_hint=(.25, .075))
            level_button.bind(on_press=self.changer)
            self.layout.add_widget(level_button)

        self.add_widget(self.layout)

    def changer(self, instance):
        level = int(instance.text.split(" ")[1])
        self.game_session.set_level(self.game_session.levels[level])
        try:
            self.game_session.game_screen.display()
        except:
            pass
        self.manager.current = 'game_screen'


class GameScreen(Screen):
    game_session = None
    level = None
    plot = None
    appliances = []
    locations = [(0.15, 0.15), (0.25, 0.15), (0.38, 0.15), (0.5, 0.15), (0.62, 0.15), (0.73, 0.15)]
    layout = FloatLayout()

    def update(self, dt):
        self.plot.points = [(x, sin(x / 10.)) for x in range(0, 101)]

    def __init__(self, game_session, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.game_session = game_session

    def display(self):
        background = Image(source="images/background2.png")
        clinic = Image(source="images/clinic.png", pos_hint={'x': .15, 'y': -0.05}, size_hint=(.7, .7))
        sun = Image(source="images/sun.png", pos_hint={'x': .15, 'y': 0.3}, size_hint=(.7, .7))

        self.layout.add_widget(background)
        self.layout.add_widget(clinic)
        self.layout.add_widget(sun)

        back_button = Button(text="<< Menu",
                              font_size='18dp',
                              pos_hint={'x': .05, 'y': 0.85},
                              size_hint=(.15, .075), on_press=self.callpopup)
        self.layout.add_widget(back_button)

        for i, appliance in enumerate(self.game_session.level.appliances):
            appliance.pos_hint = {'x': self.locations[i][0], 'y': self.locations[i][1]}
            appliance.size_hint = (.12, .12)
            self.layout.add_widget(appliance)

        graph = Graph(x_ticks_minor=5,
                      x_ticks_major=25, y_ticks_major=1,
                      y_grid_label=True, x_grid_label=True, padding=5,
                      x_grid=True, y_grid=True, xmin=-0, xmax=100, ymin=-1, ymax=1,
                      pos_hint={'x': .7, 'y': .7}, size_hint=(.3, .3))
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        graph.add_plot(self.plot)
        self.layout.add_widget(graph)
        self.add_widget(self.layout)

    def callpopup(self, event):
        dlg = MessageBox(self, titleheader="Confirm", message="Are sure you want to quit the game",
                         options={"YES": "yes()", "NO": "no()"})

    def yes(self):
        self.game_session.level = None
        self.manager.current = 'welcome_screen'

    def no(self):
        pass


class EnergyGameApp(App):
    def build(self):

        game_session = GameSession()
        with open('levels.json') as data_file:
            levels = json.load(data_file)
            for level in levels:
                this_level = Level(level['name'])
                appliances = []
                for appliance in level['appliances']:
                    appliances.append(Appliance(appliance['type'], appliance['icon'], appliance['rating']))
                this_level.appliances = appliances
                game_session.add_level(this_level)

        welcome_screen = WelcomeScreen(game_session, name='welcome_screen')
        game_screen = GameScreen(game_session, name='game_screen')

        game_session.set_welcome_screen(welcome_screen)
        game_session.set_game_screen(game_screen)

        screen_manager = ScreenManager()
        screen_manager.add_widget(welcome_screen)
        screen_manager.add_widget(game_screen)

        return screen_manager

    def set_state(self, state):
        if state == 'main_game':
            self.root.current = 'main_game'
            game = self.root.energy_game
            game.initialise(0)
            Clock.schedule_interval(game.update, 1.0 / 60.0)


class MessageBox(EnergyGameApp):
    def __init__(self, parent, titleheader="Title", message="Message", options={"OK": ""}, size=(400, 400)):

        def popup_callback(instance):
            "callback for button press"
            self.retvalue = instance.text
            self.popup.dismiss()

        self.parent = parent
        self.retvalue = None
        self.titleheader = titleheader
        self.message = message
        self.options = options
        self.size = size
        box = GridLayout(orientation='vertical', cols=1)
        box.add_widget(Label(text=self.message, font_size=16))
        b_list = []
        buttonbox = BoxLayout(orientation='horizontal')
        for b in self.options:
            b_list.append(Button(text=b, size_hint=(1,.35), font_size=20))
            b_list[-1].bind(on_press=popup_callback)
            buttonbox.add_widget(b_list[-1])
        box.add_widget(buttonbox)
        self.popup = Popup(title=titleheader, content=box, size_hint=(None, None), size=self.size)
        self.popup.open()
        self.popup.bind(on_dismiss=self.OnClose)

    def OnClose(self, event):
        self.popup.unbind(on_dismiss=self.OnClose)
        self.popup.dismiss()
        if self.retvalue and self.options[self.retvalue] != "":
            command = "self.parent."+self.options[self.retvalue]
            exec command

if __name__ == "__main__":
    EnergyGameApp().run()
