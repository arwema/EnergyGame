from kivy.uix.popup import Popup
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
import json
import random
from kivy.clock import Clock
from kivy.config import Config
from kivy.graphics import Rectangle, Color
from kivy.uix.screenmanager import Screen, ScreenManager
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')


class GameSession:
    def __init__(self, level, start_hour, duration):
        self.time = start_hour * 3600
        self.level = level
        self.duration = duration
        self.current_load = 0
        self.iteration = 0
        self.battery = 0
        self.rain = []

    def current_time(self):
        return self.time / 3600, (self.time / 60) % 60, self.time % 60

    def set_current_load(self):
        load = 0
        if self.level:
            for appliance in self.level.appliances:
                if appliance.state == 'down':
                    load += int(appliance.rating)
        self.current_load = load


class Level:

    def __init__(self, name):
        self.name = name
        self.appliances = []
        self.supply = []
        self.battery = 0

    @staticmethod
    def make_level(json):
        level = Level(json['name'])
        level.supply = json['supply']
        level.battery = json['battery']
        for appliance in json['appliances']:
            level.appliances.append(Appliance(appliance['type'], appliance['icon'], appliance['rating']))
        return level


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
    json_levels = None
    with open('levels.json') as data_file:
        json_levels = json.load(data_file)

    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        background = Image(source="images/background2.png")
        self.layout.add_widget(background)
        welcome_label = Label(text="Energy Game",
                            font_size='48dp',
                            pos_hint={'x': .4, 'y': .8},
                            size_hint=(.2, .1))
        self.layout.add_widget(welcome_label)
        duration_label = Label(text="Duration (Min)",
                              font_size='16dp',
                              pos_hint={'x': .34, 'y': .64},
                              size_hint=(.2, .1))
        self.layout.add_widget(duration_label)
        self.duration = TextInput(text="10", pos_hint={'x': .52, 'y': .65}, size_hint=(.1, .07))
        self.layout.add_widget(self.duration)
        for i, level in enumerate(WelcomeScreen.json_levels):
            level_button = Button(text=level['name'],
                          font_size='18dp',
                          pos_hint={'x': .375, 'y': 0.55 - (i * 0.076)},
                          size_hint=(.25, .075))
            level_button.bind(on_press=self.changer)
            self.layout.add_widget(level_button)

        self.add_widget(self.layout)

    def changer(self, instance):
        level = Level.make_level(WelcomeScreen.json_levels[int(instance.text.split(" ")[1])])
        duration = int(self.duration.text)
        game_session = GameSession(level, 6, duration)
        game_screen = GameScreen(game_session, name="game_screen")
        game_screen.display()
        self.manager.add_widget(game_screen)
        self.manager.current = 'game_screen'


class GameScreen(Screen):

    def __init__(self, game_session, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.time_label = None
        self.current_load_label = None
        self.load_plot = None
        self.locations = [(0.15, 0.15), (0.25, 0.15), (0.38, 0.15), (0.5, 0.15), (0.62, 0.15), (0.73, 0.15)]
        self.layout = FloatLayout()
        self.game_session = game_session
        self.current_load_label = Label(text=str(self.game_session.current_load))

    def display(self):
        background = Image(source="images/background2.png")
        clinic = Image(source="images/clinic.png", pos_hint={'x': .15, 'y': -0.05}, size_hint=(.7, .7))
        sun = Image(source="images/sun.png", size_hint=(.7, .7))
        sun.pos_hint = {'x': .15, 'y': 0.3};

        self.layout.add_widget(background)
        self.layout.add_widget(clinic)
        self.layout.add_widget(sun)

        if self.game_session.level.battery > 0:
            battery = Image(source="images/battery.png", size_hint=(.3, .38), pos_hint={'x': .1, 'y': .2})
            self.layout.add_widget(battery)

        self.time_label = Label(text="00:00:00",
                           font_size='24dp',
                           pos_hint={'x': .4, 'y': .01},
                           size_hint=(.2, .1))
        self.layout.add_widget(self.time_label)

        back_button = Button(text="<< Menu",
                              font_size='18dp',
                              pos_hint={'x': .01, 'y': 0.01},
                              size_hint=(.15, .075), on_press=self.callpopup)
        self.layout.add_widget(back_button)

        for i, appliance in enumerate(self.game_session.level.appliances):
            appliance.pos_hint = {'x': self.locations[i][0], 'y': self.locations[i][1]}
            appliance.size_hint = (.12, .12)
            self.layout.add_widget(appliance)

        self.layout.add_widget(self.current_load_label)
        self.add_widget(self.layout)
        Clock.schedule_interval(self.update, 1)
        Clock.schedule_interval(self.add_drop, 1/20)
        Clock.schedule_interval(self.move_rain, 1/20)

    def add_drop(self, dt):
        drop = Drop()
        self.game_session.rain.append(drop)
        self.layout.add_widget(drop)

    def move_rain(self, dt):
        for i, drop in enumerate(self.game_session.rain):
            drop.pos_hint = {'y': drop.pos_hint.get('y') - .01, 'x': drop.pos_hint.get('x')}
            if drop.pos_hint.get('y') < 0:
                self.layout.remove_widget(drop)
                del self.game_session.rain[i]
                del drop

    def update(self, dt):
        current_time = self.game_session.current_time()
        current_supply = self.game_session.level.supply[current_time[0]]
        current_load = self.game_session.current_load
        balance = current_supply - current_load

        hour = ("0"+str(current_time[0]))[-2:]
        min = ("0"+str(current_time[1]))[-2:]
        sec = ("0"+str(current_time[2]))[-2:]

        self.time_label.text = "%s:%s:%s" % (hour, min, sec)
        self.game_session.time += (12 * 60) / self.game_session.duration
        self.game_session.set_current_load()
        self.current_load_label.text = str(self.game_session.current_load)

        rect_width = 5
        rect_height = 100
        full_height = 480
        space = 1

        with self.layout.canvas:
            # plot supply
            Color(0, 1, 0, 1.0, mode='rgba')
            Rectangle(pos=(self.game_session.iteration * (rect_width + space), full_height - rect_height),
                      size=(rect_width, self.game_session.level.supply[current_time[0]]/rect_height))
            # plot load
            Color(0, 0, 1, 1.0, mode='rgba')
            Rectangle(pos=(self.game_session.iteration * (rect_width + space), full_height - rect_height),
                      size=(rect_width, self.game_session.current_load/rect_height))

            # plot overload (battery used)
            Color(1, 0, 1, 1.0, mode='rgba')
            if balance < 0:
                Rectangle(pos=(self.game_session.iteration * (rect_width + space), full_height - rect_height + current_load / rect_height),
                          size=(rect_width, balance/rect_height))
        self.game_session.iteration += 1

    def callpopup(self, event):
        MessageBox(self, titleheader="Confirm", message="Are sure you want to quit the game",
                         options={"YES": "yes()", "NO": "no()"})

    def yes(self):
        self.game_session.level = None
        self.manager.current = 'welcome_screen'
        # Todo: Clock unschedule
        self.manager.remove_widget(self)


    def no(self):
        pass


class EnergyGameApp(App):
    def build(self):
        screen_manager = ScreenManager()
        welcome_screen = WelcomeScreen(name='welcome_screen')
        screen_manager.add_widget(welcome_screen)

        return screen_manager


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


class Drop(Image):
    def __init__(self, **kwargs):
        super(Drop, self).__init__(source="images/droplet.png", size_hint=(.3, .38), pos_hint={'x': random.random(), 'y': .8})

if __name__ == "__main__":
    EnergyGameApp().run()
