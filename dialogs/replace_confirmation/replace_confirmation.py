#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017, 2018 Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class ReplaceConfirmationDialog(object):
    ''' This dialog is asking users if they really want to do a replace all. '''

    def __init__(self, main_window):
        self.main_window = main_window

    def run(self, original, replacement, number_of_occurences):
        self.setup(original, replacement, number_of_occurences)
        response = self.view.run()
        if response == Gtk.ResponseType.YES:
            return_value = True
        else:
            return_value = False
        self.view.hide()
        del(self.view)
        return return_value

    def setup(self, original, replacement, number_of_occurences):
        self.view = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.QUESTION)

        plural = 's' if number_of_occurences > 1 else ''
        self.view.set_property('text', 'Replacing ' + str(number_of_occurences) + ' occurence' + plural + ' of »' + original + '« with »' + replacement + '«.')
        self.view.format_secondary_markup('Do you really want to do this?')

        self.view.add_buttons('_Cancel', Gtk.ResponseType.CANCEL, '_Yes, replace all occurences', Gtk.ResponseType.YES)
        self.view.set_default_response(Gtk.ResponseType.YES)


