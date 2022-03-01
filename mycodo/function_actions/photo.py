# coding=utf-8
from flask_babel import lazy_gettext

from mycodo.config_translations import TRANSLATIONS
from mycodo.databases.models import Actions
from mycodo.databases.models import Camera
from mycodo.devices.camera import camera_record
from mycodo.function_actions.base_function_action import AbstractFunctionAction
from mycodo.utils.database import db_retrieve_table_daemon

FUNCTION_ACTION_INFORMATION = {
    'name_unique': 'photo',
    'name': '{}: {}'.format(TRANSLATIONS['camera']['title'], lazy_gettext('Capture Photo')),
    'library': None,
    'manufacturer': 'Mycodo',

    'url_manufacturer': None,
    'url_datasheet': None,
    'url_product_purchase': None,
    'url_additional': None,

    'message': lazy_gettext('Capture a photo with the selected Camera.'),

    'usage': 'Executing <strong>self.run_action("{ACTION_ID}")</strong> will capture a photo with the selected Camera. '
             'Executing <strong>self.run_action("{ACTION_ID}", value={"camera_id": "959019d1-c1fa-41fe-a554-7be3366a9c5b"})</strong> will capture a photo with the Camera with the specified ID.',

    'dependencies_module': [],

    'custom_options': [
        {
            'id': 'controller',
            'type': 'select_device',
            'default_value': '',
            'options_select': [
                'Camera'
            ],
            'name': lazy_gettext('Camera'),
            'phrase': 'Select the Camera to take a photo'
        }
    ]
}


class ActionModule(AbstractFunctionAction):
    """Function Action: Capture Photo."""
    def __init__(self, action_dev, testing=False):
        super(ActionModule, self).__init__(action_dev, testing=testing, name=__name__)

        self.controller_id = None

        action = db_retrieve_table_daemon(
            Actions, unique_id=self.unique_id)
        self.setup_custom_options(
            FUNCTION_ACTION_INFORMATION['custom_options'], action)

        if not testing:
            self.setup_action()

    def setup_action(self):
        self.action_setup = True

    def run_action(self, message, dict_vars):
        try:
            controller_id = dict_vars["value"]["camera_id"]
        except:
            controller_id = self.controller_id

        this_camera = db_retrieve_table_daemon(
            Camera, unique_id=controller_id, entry='first')

        if not this_camera:
            msg = " Error: Camera with ID '{}' not found.".format(controller_id)
            message += msg
            self.logger.error(msg)
            return message

        message += "  Capturing photo with camera {unique_id} ({id}, {name}).".format(
            unique_id=controller_id,
            id=this_camera.id,
            name=this_camera.name)

        camera_record('photo', controller_id)

        self.logger.debug("Message: {}".format(message))

        return message

    def is_setup(self):
        return self.action_setup