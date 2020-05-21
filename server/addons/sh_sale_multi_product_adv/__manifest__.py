# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Advance Product Search and Selection in sale order",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "category": "Sales",
    "summary": "This module is very useful to select products on basis of different filters.",
    "description": """
    
Do you having lots of products and variants? Feeling difficulty to filter/search and choose specific products in sale orders?
So here we come with solution, Our module will help you to filter products with fully customized your favourite products fields and variant attributes.
Our module will save your time and efforts for selection of products on basis of different criterias.

We have provided configuration of products fields and attributes. 
You can easily customized it as you required. After configurations of your favourites fields and attributes you will be able to add products on basis of that customized fields and attributes criterias or patterns.

Cheers! 


                    """,    
    "version":"11.0.3",
    "depends" : ["base","sale","sale_management","product","stock"],
    "application" : True,
    "data" : ['views/settings_view.xml',
              'wizard/smps_wizard.xml',
              'views/sale_view.xml',              
            ],            
    "images": ["static/description/background.png",],              
    "auto_install":False,
    "installable" : True,
    "price": 50,
    "currency": "EUR"   
}
