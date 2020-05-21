<?xml version="1.0"?>
<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
<flectra>
    <data>
        %for action in object['action_window_ids']:
          ${mako_stuffs.module_builder_action_window_ids(action)}
        %endfor
    </data>
</flectra>