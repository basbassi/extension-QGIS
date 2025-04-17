def classFactory(iface):
    from .altitude_diff_plugin import AltitudeDiffPlugin
    return AltitudeDiffPlugin(iface)
