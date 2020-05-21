<?xml version="1.0"?>
<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
<flectra>
    <data>
        %for view in object['view_ids']:
          ${mako_stuffs.module_builder_ir_ui_view(view)}
        %endfor
    </data>
</flectra>