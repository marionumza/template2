<?xml version="1.0"?>
<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
<flectra>
    <data>
        %for group in object['groups']:
          ${mako_stuffs.module_builder_res_groups(group)}
        %endfor
    </data>
    <data noupdate="1">
        %for rule in object['rules']:
          ${mako_stuffs.module_builder_ir_rule(rule)}
        %endfor
    </data>
</flectra>