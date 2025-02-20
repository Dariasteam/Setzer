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

import setzer.document.latex.build_system.query.query as query
from setzer.app.service_locator import ServiceLocator


class BuildSystemController(object):
    ''' Mediator between document and build_system. '''
    
    def __init__(self, document, build_system):
        self.document = document
        self.build_system = build_system
        self.settings = ServiceLocator.get_settings()

        self.document.connect('build_state_change', self.on_build_state_change)

    def on_build_state_change(self, document, parameter):
        if parameter == 'ready_for_building':
            document = self.document
            mode = document.get_build_mode()
            query_obj = query.Query(self.document.get_filename()[:])

            if mode in ['forward_sync', 'build_and_forward_sync']:
                synctex_arguments = self.document.forward_sync_arguments

            if mode in ['build', 'build_and_forward_sync']:
                interpreter = self.settings.get_value('preferences', 'latex_interpreter')
                use_latexmk = self.settings.get_value('preferences', 'use_latexmk')
                build_option_system_commands = self.settings.get_value('preferences', 'build_option_system_commands')
                additional_arguments = ''

                lualatex_prefix = ' -' if interpreter == 'lualatex' else ' '
                if build_option_system_commands == 'disable':
                    additional_arguments += lualatex_prefix + '-no-shell-escape'
                elif build_option_system_commands == 'restricted':
                    additional_arguments += lualatex_prefix + '-shell-restricted'
                elif build_option_system_commands == 'enable':
                    additional_arguments += lualatex_prefix + '-shell-escape'

                text = document.get_text()
                do_cleanup = self.settings.get_value('preferences', 'cleanup_build_files')

            if mode == 'build':
                query_obj.jobs = ['build_latex']
                query_obj.build_data['text'] = text
                query_obj.build_data['latex_interpreter'] = interpreter
                query_obj.build_data['use_latexmk'] = use_latexmk
                query_obj.build_data['additional_arguments'] = additional_arguments
                query_obj.build_data['do_cleanup'] = do_cleanup
            elif mode == 'forward_sync':
                query_obj.jobs = ['forward_sync']
                query_obj.can_sync = True
                query_obj.forward_sync_data['filename'] = synctex_arguments['filename']
                query_obj.forward_sync_data['line'] = synctex_arguments['line']
                query_obj.forward_sync_data['line_offset'] = synctex_arguments['line_offset']
            elif mode == 'backward_sync' and document.backward_sync_data != None:
                query_obj.jobs = ['backward_sync']
                query_obj.can_sync = True
                query_obj.backward_sync_data['page'] = document.backward_sync_data['page']
                query_obj.backward_sync_data['x'] = document.backward_sync_data['x']
                query_obj.backward_sync_data['y'] = document.backward_sync_data['y']
                query_obj.backward_sync_data['word'] = document.backward_sync_data['word']
                query_obj.backward_sync_data['context'] = document.backward_sync_data['context']
            else:
                query_obj.jobs = ['build_latex', 'forward_sync']
                query_obj.build_data['text'] = text
                query_obj.build_data['latex_interpreter'] = interpreter
                query_obj.build_data['use_latexmk'] = use_latexmk
                query_obj.build_data['additional_arguments'] = additional_arguments
                query_obj.build_data['do_cleanup'] = do_cleanup
                query_obj.can_sync = False
                query_obj.forward_sync_data['filename'] = synctex_arguments['filename']
                query_obj.forward_sync_data['line'] = synctex_arguments['line']
                query_obj.forward_sync_data['line_offset'] = synctex_arguments['line_offset']

            self.build_system.add_query(query_obj)

        if parameter == 'building_to_stop':
            self.build_system.stop_building()


