tool = [   {   'function': {   'description': 'Executes a terminal command in the '
                                       'current working directory.',
                        'name': 'use_terminal',
                        'parameters': {   'properties': {   'text': {   'type': 'string'}},
                                          'required': ['text'],
                                          'type': 'object'}},
        'type': 'function'},
    {   'function': {   'description': 'Perform GUI actions such as moving the '
                                       'mouse, clicking, typing, pressing '
                                       'keys, hotkeys, and scrolling using '
                                       'pyautogui.',
                        'name': 'gui_control',
                        'parameters': {   'properties': {   'action': {   'description': 'The '
                                                                                         'GUI '
                                                                                         'action '
                                                                                         'to '
                                                                                         'perform '
                                                                                         '(move, '
                                                                                         'click, '
                                                                                         'double_click, '
                                                                                         'right_click, '
                                                                                         'typewrite, '
                                                                                         'press, '
                                                                                         'hotkey, '
                                                                                         'scroll).',
                                                                          'enum': [   'move',
                                                                                      'click',
                                                                                      'double_click',
                                                                                      'right_click',
                                                                                      'typewrite',
                                                                                      'press',
                                                                                      'hotkey',
                                                                                      'scroll'],
                                                                          'type': 'string'},
                                                            'button': {   'default': 'left',
                                                                          'description': 'Mouse '
                                                                                         'button '
                                                                                         'to '
                                                                                         'use '
                                                                                         '(left, '
                                                                                         'right, '
                                                                                         'middle).',
                                                                          'enum': [   'left',
                                                                                      'right',
                                                                                      'middle'],
                                                                          'type': 'string'},
                                                            'clicks': {   'default': 1,
                                                                          'description': 'Number '
                                                                                         'of '
                                                                                         'clicks '
                                                                                         '(default '
                                                                                         '1).',
                                                                          'type': 'integer'},
                                                            'duration': {   'default': 0.0,
                                                                            'description': 'Duration '
                                                                                           'for '
                                                                                           'mouse '
                                                                                           'movement '
                                                                                           '(seconds).',
                                                                            'type': 'number'},
                                                            'interval': {   'default': 0.0,
                                                                            'description': 'Interval '
                                                                                           'between '
                                                                                           'clicks '
                                                                                           '(seconds).',
                                                                            'type': 'number'},
                                                            'keys': {   'description': 'List '
                                                                                       'of '
                                                                                       'keys '
                                                                                       'for '
                                                                                       'hotkey '
                                                                                       'action.',
                                                                        'items': {   'type': 'string'},
                                                                        'type': 'array'},
                                                            'scroll': {   'description': 'Amount '
                                                                                         'to '
                                                                                         'scroll '
                                                                                         '(positive '
                                                                                         'for '
                                                                                         'up, '
                                                                                         'negative '
                                                                                         'for '
                                                                                         'down).',
                                                                          'type': 'integer'},
                                                            'text': {   'description': 'Text '
                                                                                       'to '
                                                                                       'type '
                                                                                       'or '
                                                                                       'key '
                                                                                       'to '
                                                                                       'press '
                                                                                       'for '
                                                                                       'certain '
                                                                                       'actions.',
                                                                        'type': 'string'},
                                                            'x': {   'description': 'X '
                                                                                    'coordinate '
                                                                                    'for '
                                                                                    'mouse '
                                                                                    'actions '
                                                                                    '(optional).',
                                                                     'type': 'integer'},
                                                            'y': {   'description': 'Y '
                                                                                    'coordinate '
                                                                                    'for '
                                                                                    'mouse '
                                                                                    'actions '
                                                                                    '(optional).',
                                                                     'type': 'integer'}},
                                          'required': ['action'],
                                          'type': 'object'}},
        'type': 'function'}]

__all__ = ["tool"]


