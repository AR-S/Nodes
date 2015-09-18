import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.properties import ObjectProperty, BooleanProperty, NumericProperty
from kivy.config import Config
from kivy.animation import Animation
from kivy.clock import Clock

from simpleOSC import initOSCClient, initOSCServer, closeOSC, \
        setOSCHandler, sendOSCMsg
import pygame.midi


class BrokerControlButton(Button):
    '''Custom button class for having his index and custom graphics defined in
    the .kv + highligh state that draw an hover when activated.
    '''
    highlight = BooleanProperty(False)
    index = NumericProperty(0)


class BrokerControlMain(FloatLayout):
    '''Main panel containing all the buttons and sliders.
    The layout is done in the .kv, and assign each part of the UI to grid,
    grid_right, grid_bottom, grid_xy.
    '''

    app = ObjectProperty(None)
    grid = ObjectProperty(None)
    grid_right = ObjectProperty(None)
    grid_bottom = ObjectProperty(None)
    grid_xy = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(BrokerControlMain, self).__init__(**kwargs)

        # create and bind every slider and buttons
        for x in xrange(1, 11):
            btn = BrokerControlButton(index=x, text=str(x))
            btn.bind(state=self.on_button_state)
            self.grid.add_widget(btn)

        # led handler for monome
        prefix = self.app.config.get('monome', 'prefix')
        setOSCHandler('/%s/led' % prefix, self.on_led)
        setOSCHandler('/%s/led_col' % prefix, self.on_led_col)
        setOSCHandler('/%s/led_row' % prefix, self.on_led_row)
        setOSCHandler('/%s/led_frame' % prefix, self.on_led_frame)
        setOSCHandler('/%s/led_clear' % prefix, self.on_led_clear)

        # empty handlers
        setOSCHandler('/sys/prefix', self.empty_handler)
        setOSCHandler('/sys/cable', self.empty_handler)
        setOSCHandler('/sys/offset', self.empty_handler)
        setOSCHandler('/sys/intensity', self.empty_handler)
        setOSCHandler('/sys/test', self.empty_handler)
        setOSCHandler('/sys/report', self.empty_handler)

    def on_button_state(self, instance, value):
        prefix = self.app.config.get('monome', 'prefix')
        index = instance.index
        value = 1 if value == 'down' else 0
        #sendOSCMsg('/%s/press' % prefix, [index % 8, index / 8, value])
        print('/%s/press' % index, [index % 8, index / 8, value])

    def on_bottom_slider_value(self, instance, value):
        pass
        #midi_out = self.app.midi_out
        #midi_out.write_short(0xb0, instance.index, int(value))

    def on_right_slider_value(self, instance, value):
        pass
        #midi_out = self.app.midi_out
        #midi_out.write_short(0xba, instance.index, int(value))

    def on_led(self, addr, tags, data, source):
        x, y, s =data[0:3]
        index = 63-int((x + y) + (y * 7))
        print index
        self.grid.children[index].highlight = bool(s)

    def on_led_col(self, addr, tags, data, source):
        col, cv = data[0:2]
        colvals = map(int, (list(''.join([str((cv>> y) & 1) for y in xrange(7, -1, -1)]))))
        colvals.reverse()
        for i in xrange(8):
            index = int(col + (8 * i))
            self.grid.children[index].highlight = (colvals[i] > 0)

    def on_led_row(self, addr, tags, data, source):
        row, rv = data[0:2]
        rowvals = map(int, (list(''.join([str((rv>> y) & 1) for y in xrange(7, -1, -1)]))))
        rowvals.reverse()
        for i in xrange(8):
            index = int(row) * 8 + i
            self.grid.children[index].highlight = (rowvals[i] > 0)

    def on_led_frame(self, addr, tags, data, source):
        for i in xrange(8):
            rv = data[i]
            rowvals = (map(int, (list("".join([str((rv>> y) & 1) for y in range(7, -1, -1)])))))
            rowvals.reverse()
            for n in xrange(8):
                index = i * 8 + n
                self.grid.children[index].highlight = rowvals[n] > 0

    def on_led_clear(self, addr, tags, data, source):
        x = data[0]
        for i in xrange(64):
            self.grid.children[i] = (x == 1)

    def empty_handler(self, *largs):
        pass


class BrokerSplash(FloatLayout):
    app = ObjectProperty(None)


class BrokerControlApp(App):
    def build(self):
        Clock.schedule_once(lambda dt: self.do_connect(), 7)
        return BrokerSplash(app=self)

    def build_config(self, config):
        config.add_section('arduino')
        config.set('arduino', 'device', '/dev/ttyUSB0')
        config.add_section('network')
        config.set('network', 'port', '2525')

    def build_settings(self, settings):
        data = '''[
            { "type": "title", "title": "Arduino Configuration" },
            { "type": "options", 
              "title": "Device",
              "desc": "Path to Arduino device resource",
              "section": "arduino", 
              "options": ["/dev/ttyUSB0", "/dev/wchusb0AE03", "/dev/tty.usba223a"],
              "key": "device" },

            { "type": "title", "title": "OSC Listening Node" },
            { "type": "numeric", "title": "Port",
              "desc": "Listen to incoming OSC messages on port",
              "section": "network", "key": "port" }
        ]'''
        settings.add_json_panel('AR.S Total Control', self.config, data=data)

    def on_stop(self):
        closeOSC()

    def do_connect(self):
        config = self.config
        host = config.get('network', 'host')
        sport = config.getint('monome', 'send_port')
        rport = config.getint('monome', 'receive_port')
        mdevice = config.getint('midi', 'device')
        # osc
        initOSCClient(host, sport)
        initOSCServer(host, rport)
        # midi
        #pygame.midi.init()
        #pygame.midi.get_count()
        #self.midi_out = pygame.midi.Output(device_id=mdevice)
        #self.device_name = pygame.midi.get_device_info(mdevice)

        # switch to main screen
        parent = self.root.parent
        parent.remove_widget(self.root)
        self.root = BrokerControlMain(app=self)
        parent.add_widget(self.root)


if __name__ in ('__main__', '__android__'):
    try:
        Config.set('graphics', 'width', '320')
        Config.set('graphics', 'height', '240')
        BrokerControlApp().run()
    finally:
        closeOSC()
