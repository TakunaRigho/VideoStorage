#coding: utf-8


import copy
from json import dumps
from ConfigParser import RawConfigParser
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from apps.server.models import Config
from apps.server.models import DfCommand
from apps.server.models import Uptime
from apps.server.models import Status


class TestConfigCreater(object):
    filename = "config.test"

    section = 'MAIN'

    options = (
        ('header', 'value'),
        ('header2', 'value2'),
        ('header3', 'value3'),
    )

    def __init__(self):
        self.config = RawConfigParser()
        self.config.read(self.filename)

        if not self.config.has_section(self.section):
            self.config.add_section(self.section)

        for option in self.options:
            header, value = option
            self.config.set(self.section, header, value)

        with open(self.filename, 'w') as f:
            self.config.write(f)


class TestConfigModel(TestCase):
    filename = "config.test"

    std_cfg = [
        {
            'name': 'MAIN',
            'items': [
                dict(header='header', value='value'),
                dict(header='header2', value='value2'),
                dict(header='header3', value='value3'),
            ]
        }
    ]

    def setUp(self):
        TestConfigCreater()
        self.config = Config(self.filename)

    def test_to_dict(self):
        to_dict = self.config.to_dict()
        self.assertEqual(to_dict, self.std_cfg)

    def test_delete(self):
        mutate_cfg = copy.deepcopy(self.std_cfg) # remove row from items on
        mutate_cfg[0]['items'] = mutate_cfg[0]['items'][1:]
        self.config.delete(*('MAIN', 'header'))
        to_dict = self.config.to_dict()
        self.assertEqual(to_dict, mutate_cfg)

    def test_edit(self):
        mutate_cfg = copy.deepcopy(self.std_cfg)
        mutate_cfg[0]['items'][0] = dict(header='header', value='value23') # change row from items on dict(header='header23', value='value23')
        self.config.edit(*('MAIN', 'header', 'value23'))
        to_dict = self.config.to_dict()
        self.assertEqual(to_dict, mutate_cfg)


class TestCommand(TestCase):

    client = Client()

    def test_df(self):
        cmd = DfCommand()
        print cmd()

    def test_uptime(self):
        cmd = Uptime()
        print cmd()

    def test_status(self):
        cmd = Status()
        print cmd()

    def test_info_view(self):
        url = reverse('info')
        response = self.client.get(url)
        print response.content


class TestConfigView(TestCase):

    client = Client()

    def setUp(self):
        TestConfigCreater()

    def test_config_view(self):
        url = reverse('config')
        response = self.client.get(url, dict(action='static'))
        expected_data = dumps(TestConfigModel.std_cfg)
        self.assertJSONEqual(response.content, expected_data)
        print response.content, expected_data

    def test_config_delete(self):
        url = reverse('config')
        response = self.client.get(url, dict(action='delete', section="MAIN", option="header"))
        self.assertContains(response, 'ok')

    def test_config_delete(self):
        url = reverse('config')
        response = self.client.get(url, dict(action='edit', section="MAIN", option="header", value="header23"))
        self.assertContains(response, 'ok')


class TestControlView(TestCase):

    client = Client()

    def test_control_start(self):
        url = reverse('control')
        response = self.client.get(url, {'action': 'start'})
        print response.content
