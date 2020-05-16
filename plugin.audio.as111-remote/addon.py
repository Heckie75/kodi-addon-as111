#!/usr/bin/python3
import json
import os
import os.path
import subprocess
import sys
import urlparse

import xbmcgui
import xbmcplugin
import xbmcaddon

__PLUGIN_ID__ = "plugin.audio.as111-remote"

settings = xbmcaddon.Addon(id=__PLUGIN_ID__)
addon_handle = int(sys.argv[1])
addon_dir = xbmc.translatePath( settings.getAddonInfo('path') )




def _get_entries(alias, vol):

    entries = [
        {
            "path" : "status",
            "name" : "%s: Volume is %s" % (alias, vol if vol != 0 else "muted"),
            "icon" : "icon_info"
        },
        {
            "path" : "up",
            "name" : "Volume up",
            "icon" : "icon_sound_up",
            "exec" : ["vol", "%2B1"]
        },
        {
            "path" : "down",
            "name" : "Volume down",
            "icon" : "icon_sound_down",
            "exec" : ["vol", "-1"]
        },
        {
            "path" : "mute",
            "name" : "%s" % "Mute" if vol != 0 else "[COLOR orange]Mute[/COLOR]",
            "icon" : "icon_mute",
            "exec" : ["mute"]
        }
    ]

    _min = int(settings.getSetting("vol_min"))
    _max = int(settings.getSetting("vol_max")) + 1

    icons = ["icon_low", "icon_medium", "icon_full"]
    icon_div = (_max - _min) / (1.0 * len(icons))

    _range = range(_min, _max)
    for i in _range:

        if vol == i:
            name ="[COLOR orange]Volume %i[/COLOR]" % i
        else:
            name ="Volume %i" % i

        entries += [
            {
                "path" : str(i),
                "name" : name,
                "icon" : icons[int(((i - _min) / icon_div))],
                "exec" : ["vol", str(i)]
            }
        ]

    return entries




def _parse_status(_json):

    status = json.loads(_json)
    alias = status["alias"] if status["alias"] != "" else status["name"]
    vol = status["volume"]

    return alias, vol




def _build_menu(alias = None, vol = None):

    if vol == None:
        out = _exec_as111([ "json" ])
        alias, vol = _parse_status(out)

    entries = _get_entries(alias, vol)
    for entry in entries:
        _add_list_item(entry)

    xbmcplugin.endOfDirectory(addon_handle)




def _build_param_string(param, values):

    current = ""
    for v in values:
        current += "|" if len(current) == 0 else "&"
        current += param + "=" + v

    return current




def _add_list_item(entry):

    item_path = "/" + entry["path"]
    if "exec" in entry:
        param_string = _build_param_string(
            param = "exec",
            values = entry["exec"])
    else:
        param_string = ""

    icon_file = os.path.join(addon_dir, "resources", "assets", entry["icon"] + ".png")
    li = xbmcgui.ListItem(entry["name"], iconImage=icon_file)
    xbmcplugin.addDirectoryItem(handle=addon_handle,
                            listitem=li,
                            url="plugin://" + __PLUGIN_ID__
                            + item_path
                            + param_string,
                            isFolder=False)




def _exec_as111(params):

    call = [addon_dir + os.sep + "lib" + os.sep + "as111.py"]
    call += [ "-" ] + params

    xbmc.log(" ".join(call), xbmc.LOGNOTICE)
    p = subprocess.Popen(call,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    out, err = p.communicate()
    xbmc.log(out, xbmc.LOGNOTICE)
    return out.decode("utf-8")




def _parse_url(url):

    i = url.find("|")
    if i < 0:
        return []

    param_string = url[i+1:]
    url_params = urlparse.parse_qs(param_string)

    return url_params




if __name__ == "__main__":

    url_params = _parse_url(sys.argv[0])

    if "exec" in url_params:
        out = _exec_as111(url_params["exec"] + [ "json" ])
        alias, vol = _parse_status(out)
        xbmc.executebuiltin('Container.Refresh("plugin://%s/|alias=%s&vol=%i")'
            % (__PLUGIN_ID__, alias, vol))
    elif "vol" in url_params:
        _build_menu(url_params["alias"][0], int(url_params["vol"][0]))
    else:
        _build_menu()
