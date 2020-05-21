<?xml version="1.0"?>
<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
<flectra>
    <data>
        %for cron in object['cron_ids']:
          ${mako_stuffs.module_builder_ir_cron(cron)}
        %endfor
    </data>
</flectra>