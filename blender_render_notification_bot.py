bl_info = {
    "name": "Blender Render Notification Bot",
    "blender": (3, 5, 0,),
    "category": "Render",
    "author": "Bohdan Donchyk",
    "description": "Sends a Telegram message whenever your render is finished."
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import Operator, AddonPreferences
import requests
import json
import re

class RenderNotifParams(bpy.types.Operator):
    """Set the Telegram bot token and chat ID"""  # Use this as a tooltip for menu items and buttons.
    bl_idname = "wm.rendernotifparams"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Set Telegram bot token and chat ID"  # Display name in the interface.

    bot_token: bpy.props.StringProperty(name="Enter bot token", default="")
    chat_id: bpy.props.StringProperty(name="Enter chat ID", default="")

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__name__].preferences
        prefs.bot_token = self.bot_token
        prefs.chat_id = self.chat_id

        message = "Bot token: %s, Chat ID: %s" % (self.bot_token, self.chat_id)
        self.report({'INFO'}, message)
        print(message)
        return {'FINISHED'}

    def invoke(self, context, event):
        prefs = bpy.context.preferences.addons[__name__].preferences
        self.bot_token = prefs.bot_token
        self.chat_id = prefs.chat_id
        return context.window_manager.invoke_props_dialog(self)

class RenderNotifAddonPreferences(AddonPreferences):
    bl_idname = __name__

    bot_token: bpy.props.StringProperty(name="Bot Token", default="")
    chat_id: bpy.props.StringProperty(name="Chat ID", default="")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "bot_token")
        layout.prop(self, "chat_id")

classes = (
    RenderNotifParams,
    RenderNotifAddonPreferences,
)

def menu_func(self, context):
    self.layout.operator(RenderNotifParams.bl_idname)

@persistent
def send_notification(dummy):
    print("Render complete")

    prefs = bpy.context.preferences.addons[__name__].preferences
    bot_token = prefs.bot_token  # Enter Telegram bot token
    chat_id = prefs.chat_id  # Enter Telegram chat ID

    filename = bpy.path.basename(bpy.context.blend_data.filepath)  # get the filename
    text = "- has finished rendering."
    message = filename + text
    url = "https://api.telegram.org/bot%s/sendMessage" % bot_token
    payload = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print("Failed to send message :(")

def register():
    bpy.app.handlers.render_complete.append(send_notification)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
