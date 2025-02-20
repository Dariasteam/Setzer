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

import time

from setzer.app.service_locator import ServiceLocator
from setzer.dialogs.dialog_locator import DialogLocator


class BuildSystemPresenter(object):
    ''' Mediator between document and build_system. '''
    
    def __init__(self, document, build_system):
        self.document = document
        build_system.register_observer(self)

    '''
    *** notification handlers, get called by observed build system
    '''

    def change_notification(self, change_code, notifying_object, parameter):

        if change_code == 'building_started':
            self.document.change_build_state('building_in_progress')

        if change_code == 'reset_timer':
            self.document.build_widget.view.reset_timer()
            self.document.build_widget.view.label.set_text('0:00')

        if change_code == 'building_stopped':
            self.document.show_build_state('')
            self.document.change_build_state('idle')

        if change_code == 'building_finished':
            result_blob = parameter
            if result_blob['build'] != None or result_blob['forward_sync'] != None:
                if result_blob['build'] != None:
                    try:
                        self.document.preview.set_pdf_filename(result_blob['build']['pdf_filename'])
                    except KeyError: pass
                    self.document.add_change_code('pdf_updated')

                if result_blob['forward_sync'] != None:
                    self.document.preview.set_synctex_rectangles(result_blob['forward_sync'])
                    self.document.show_build_state('')

                if result_blob['build'] != None:
                    build_blob = result_blob['build']

                    if build_blob['error'] == 'interpreter_missing':
                        self.document.show_build_state('')
                        self.document.change_build_state('idle')
                        if DialogLocator.get_dialog('interpreter_missing').run(build_blob['error_arg']):
                            DialogLocator.get_dialog('preferences').run()
                        return

                    if build_blob['error'] == 'interpreter_not_working':
                        self.document.show_build_state('')
                        self.document.change_build_state('idle')
                        if DialogLocator.get_dialog('building_failed').run(build_blob['error_arg']):
                            DialogLocator.get_dialog('preferences').run()
                        return

                    build_blob['log_messages']['BibTeX'] = build_blob['bibtex_log_messages']
                    self.document.set_build_log_items(build_blob['log_messages'])
                    self.document.build_time = time.time() - self.document.last_build_start_time

                    error_count = self.document.get_error_count()
                    if error_count > 0:
                        error_color_rgba = ServiceLocator.get_color_manager().get_theme_color('error_color')
                        error_color = '#' + format(int(error_color_rgba.red * 255), '02x') + format(int(error_color_rgba.green * 255), '02x') + format(int(error_color_rgba.blue * 255), '02x')
                        str_errors = ngettext('<span color="{color}">Failed</span> ({amount} error)!', '<span color="{color}">Failed</span> ({amount} errors)!', error_count)
                        message = str_errors.format(color=error_color, amount=str(error_count))
                        self.document.show_build_state(message)
                    else:
                        self.document.show_build_state(_('Success!'))

                    self.document.set_has_synctex_file(build_blob['has_synctex_file'])
                    self.document.has_been_built = True

            elif result_blob['backward_sync'] != None:
                if not self.document.root_is_set:
                    if result_blob['backward_sync']['filename'] == self.document.get_filename():
                        self.document.set_synctex_position(result_blob['backward_sync'])
                elif self.document.is_root:
                    workspace = ServiceLocator.get_workspace()
                    document = workspace.open_document_by_filename(result_blob['backward_sync']['filename'])
                    if document != None:
                        document.set_synctex_position(result_blob['backward_sync'])

            self.document.change_build_state('idle')

            if result_blob['build'] != None:
                self.document.invalidate_build_log()


