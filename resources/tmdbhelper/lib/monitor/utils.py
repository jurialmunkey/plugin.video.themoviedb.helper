from tmdbhelper.lib.addon.plugin import get_condvisibility
from jurialmunkey.window import get_property


CV_USE_LOCAL_CONTAINER = "Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer)"


CV_USE_LISTITEM = (
    "!Skin.HasSetting(TMDbHelper.ForceWidgetContainer) + "
    "!Window.IsActive(script-tmdbhelper-recommendations.xml) + ["
    "!Skin.HasSetting(TMDbHelper.UseLocalWidgetContainer) | String.IsEmpty(Window.Property(TMDbHelper.WidgetContainer))] + ["
    "Window.IsVisible(movieinformation) | "
    "Window.IsVisible(musicinformation) | "
    "Window.IsVisible(songinformation) | "
    "Window.IsVisible(addoninformation) | "
    "Window.IsVisible(pvrguideinfo) | "
    "Window.IsVisible(tvchannels) | "
    "Window.IsVisible(tvguide)]")


def container_item(container='Container.'):
    return (
        'ListItem.'
        if get_condvisibility(CV_USE_LISTITEM) else
        f'{container}ListItem({{}}).'
    )


def container(widget_id=''):
    return f'Container({widget_id}).' if widget_id else 'Container.'


def widget_id(window_id):
    window_id = window_id if get_condvisibility(CV_USE_LOCAL_CONTAINER) else None
    return get_property('WidgetContainer', window_id=window_id, is_type=int)
