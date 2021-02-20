import os
from resources.lib.as111 import AS111
import xbmcgui
import xbmcaddon
import xbmcvfs

__PLUGIN_ID__ = "script.philips-as111"
addon = xbmcaddon.Addon(id=__PLUGIN_ID__)
addon_dir = xbmcvfs.translatePath(addon.getAddonInfo('path'))

if __name__ == "__main__":
    as111 = AS111()
    device = as111.get_connected_device()

    icon_file = os.path.join(addon_dir,
                             "resources",
                             "assets", "icon.png")

    if device == None:
        xbmcgui.Dialog().notification(addon.getLocalizedString(
            32005), addon.getLocalizedString(32006), icon=icon_file)
        exit(1)

    if not as111.connect(device["address"]):
        xbmcgui.Dialog().notification(addon.getLocalizedString(
            32007), addon.getLocalizedString(32006), icon=icon_file)
        exit(1)

    while True:
        options = list()
        for v in range(0, 33):
            options.append("%s %s" % (
                addon.getLocalizedString(32003), v if v > 0 else addon.getLocalizedString(32004)))

        selection = xbmcgui.Dialog().select(addon.getLocalizedString(32002) %
                                            device["alias"] if device["alias"] else addon.getLocalizedString(32001), options, preselect=int(device["volume"]))
        if selection >= 0:
            as111.set_volume(selection)
        else:
            break

    v = as111.get_connected_device()["volume"]
    xbmcgui.Dialog().notification(device["alias"] if device["alias"] else addon.getLocalizedString(32001),
                                  "%s %s" % (addon.getLocalizedString(32003), v if v > 0 else addon.getLocalizedString(32004)), icon=icon_file)

    try:
        as111.disconnect()

    except:
        pass
