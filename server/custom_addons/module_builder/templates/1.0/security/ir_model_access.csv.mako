<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
%for access in object['model_access']:
${mako_stuffs.module_builder_ir_model_access(access)}
%endfor