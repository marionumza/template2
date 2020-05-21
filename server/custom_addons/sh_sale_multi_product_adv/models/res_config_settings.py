# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from flectra import models,fields,api

class res_company(models.Model):
    _inherit = "res.company"

    sh_smps_pro_field_ids = fields.Many2many("ir.model.fields",
                                string  = "Product Fields",
                                )    
    
    sh_smps_pro_attr_ids = fields.Many2many("product.attribute",
                                string = "Product Attributes"            
                                )
    

class res_config_settings(models.TransientModel):
    _inherit = "res.config.settings"
    
   
    
    sh_smps_pro_field_ids = fields.Many2many("ir.model.fields",
                                string  = "Product Fields",
                                related = "company_id.sh_smps_pro_field_ids",
                                domain=[('model_id.model', 'in', ['product.product','product.template']),
                                        ('ttype','in',['integer','char','float','boolean','many2one','selection']),
                                        ('store','=',True)
                                    ]
                                )
    
    sh_smps_pro_attr_ids = fields.Many2many("product.attribute",
                                string = "Product Attributes",
                                related = "company_id.sh_smps_pro_attr_ids",                                            
                                )    
    
 
    
    
    
    