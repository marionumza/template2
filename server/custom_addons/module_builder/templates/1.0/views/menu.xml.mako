<?xml version="1.0"?>
<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
<flectra>
    <data>
        ${rec(object['menus'])}
    </data>
</flectra>
<%def name="rec(menus)">
    %for menu in menus:
            ${menu_rendering(menu)}
            %if menu.child_id:
            ${rec(menu.child_id)}
            %endif
    %endfor
</%def>
<%def name="menu_rendering(menu)">
    ${mako_stuffs.module_builder_ir_ui_menu(menu)}
</%def>