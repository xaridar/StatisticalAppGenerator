config_schema = {
    '$schema': 'https://json-schema.org/draft/2019-09/schema',
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'options': {
            'type': 'array',
            'items': {
                'type': 'object',
                'anyOf': [
                    {
                        'additionalProperties': False,
                        'properties': {
                            'name': {'type': 'string'},
                            'type': {'const': 'text'},
                            'optional': {
                                'type': 'boolean',
                                'default': False
                            },
                            'minlength': {
                                'type': 'number',
                                'default': 0
                            },
                            'maxlength': {
                                'type': 'number',
                                'default': None
                            }
                        },
                        'required': ['name', 'type']
                    },
                    {
                        'additionalProperties': False,
                        'properties': {
                            'name': {'type': 'string'},
                            'type': {'const': 'checkbox'},
                            'optional': {
                                'type': 'boolean',
                                'default': False
                            }
                        },
                        'required': ['name', 'type']
                    },
                    {
                        'additionalProperties': False,
                        'properties': {
                            'name': {'type': 'string'},
                            'type': {'const': 'number'},
                            'optional': {
                                'type': 'boolean',
                                'default': False
                            },
                            'min': {
                                'type': 'number',
                                'default': None
                            },
                            'max': {
                                'type': 'number',
                                'default': None
                            },
                            'integer': {
                                'type': 'boolean',
                                'default': False
                            }
                        },
                        'required': ['name', 'type']
                    },
                    {
                        'additionalProperties': False,
                        'properties': {
                            'name': {'type': 'string'},
                            'type': {'const': 'select'},
                            'optional': {
                                'type': 'boolean',
                                'default': False
                            },
                            'options': {
                                'type': 'array',
                                'items': {'type': 'string'}
                            },
                            'multiselect': {
                                'type': 'boolean',
                                'default': False
                            }
                        },
                        'required': ['name', 'type', 'options']
                    }
                ]
            },
            'default': {}
        },
        'settings': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'input_file': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'enabled': {
                            'type': 'boolean',
                            'default': True
                        },
                        'graph_input': {
                            'type': 'boolean',
                            'default': True
                        },
                        'files': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'additionalProperties': False,
                                'properties': {
                                    'name': {'type': 'string'},
                                    'x_param': {
                                        'type': 'string',
                                        'default': 'x'
                                    },
                                    'y_param': {
                                        'type': 'string',
                                        'default': 'y'
                                    }
                                },
                                'required': ['name']
                            },
                            'default': [{'name': 'file', 'x_param': 'x', 'y_param': 'y'}]
                        }
                    }
                }
            }
        }
    }
}