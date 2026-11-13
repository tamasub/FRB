"""Remote Browser's segmented destination buttons use thin 1px outlines."""
from test_remote_browser_tab_choice_visual_v76_20261101 import method, menu


def test_light_selection_and_unselected_borders_are_thin():
    choose, _ = method('_select_remote_bookmark_tab')
    widget = menu('light')
    for chosen in (True, False):
        choose(widget, chosen)
        selected = (widget.remote_bookmark_new_tab_button if chosen
                    else widget.remote_bookmark_current_tab_button)
        idle = (widget.remote_bookmark_current_tab_button if chosen
                else widget.remote_bookmark_new_tab_button)
        assert 'border:1px solid #548fc8' in selected.stylesheet
        assert 'border:1px solid #b6cfc1' in idle.stylesheet
        assert 'border:2px' not in selected.stylesheet
        assert 'border:2px' not in idle.stylesheet


def test_dark_selection_and_unselected_borders_are_thin():
    choose, _ = method('_select_remote_bookmark_tab')
    widget = menu('dark')
    for chosen in (True, False):
        choose(widget, chosen)
        selected = (widget.remote_bookmark_new_tab_button if chosen
                    else widget.remote_bookmark_current_tab_button)
        idle = (widget.remote_bookmark_current_tab_button if chosen
                else widget.remote_bookmark_new_tab_button)
        assert 'border:1px solid #83bce4' in selected.stylesheet
        assert 'border:1px solid #537468' in idle.stylesheet
