<%namespace name="mako_stuffs" file="../mako_functions.mako"/>
%for package_name in object['packages']:
from . import ${package_name.replace('x_','',1)}
%endfor
