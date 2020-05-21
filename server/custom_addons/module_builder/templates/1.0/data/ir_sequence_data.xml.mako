<?xml version="1.0"?>
    <%namespace name="mako_stuffs" file="../mako_functions.mako"/>
<flectra>
    <data>
        %for model in object['model_ids']:
            %if model.allow_sequence:
                %for i in model.field_sequence_ids:
                    ${mako_stuffs.module_builder_ir_sequence_data(i.sequence_id)}
                %endfor
            %endif
        %endfor
    </data>
</flectra>