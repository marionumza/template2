{
    "name" : "${object['module'].shortdesc}",
    %if object['module'].version:
    "version" : "${object['module'].version}",
    % endif
    %if object['module'].author:
    "author" : "${object['module'].author}",
    %endif
    %if object['module'].website:
    "website" : "${object['module'].website}",
    %endif
    %if object['module'].category_id:
    "category" : "${object['module'].category_id}",
    %endif
    "licence" : "${object['module'].license}",
    "description": """
        ${object['module'].shortdesc}
        %if object['module'].summary:
        ${object['module'].summary}
        %endif
    """,
    "depends" : ${object['module'].dependencies_as_list()},
    "data" : [
        % for item in object['data']:
        '${item}',
        %endfor
    ],
    "demo" : [],
    "installable": True,
    "auto_install": ${object['module'].auto_install},
    "application": ${object['module'].application},
}