# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from flectra import models,fields,api

class res_company(models.Model):
    _inherit = "res.company"

    sh_smps_pro_field_ids = fields.Many2many(comodel_name="ir.model.fields",
                                relation="sh_smps_pro_field_ids_rel_comp_table",
                                string  = "Product Fields",
                                )    
    
    sh_smps_pro_attr_ids = fields.Many2many(comodel_name="product.attribute",
                                relation="sh_smps_pro_attr_ids_rel_comp_table",
                                string = "Product Attributes",         
                                )


class smps_adv_settings(models.TransientModel):
    _name = "smps.adv.settings"
   
   
  
    @api.model
    def sh_get_user_company(self):
        if self.env.user.company_id:
            return self.env.user.company_id.id
        else:
            return False     
       
    @api.model
    def get_sh_smps_pro_field_ids(self):
        if self.env.user.company_id and self.env.user.company_id.sh_smps_pro_field_ids:
            return self.env.user.company_id.sh_smps_pro_field_ids.ids
        else:
            return False
       
    @api.model
    def get_sh_smps_pro_attr_ids(self):
        if self.env.user.company_id and self.env.user.company_id.sh_smps_pro_attr_ids:
            return self.env.user.company_id.sh_smps_pro_attr_ids.ids
        else:
            return False              
           
    company_id = fields.Many2one("res.company", default = sh_get_user_company)   
  
    name = fields.Char(string = "Name", default = "Search Products Settings")
   
    sh_smps_pro_field_ids = fields.Many2many("ir.model.fields",
                                string  = "Product Fields",
                                related = "company_id.sh_smps_pro_field_ids",
                                domain=[('model_id.model', 'in', ['product.product','product.template']),
                                        ('ttype','in',['integer','char','float','boolean','many2one','selection']),
                                        ('store','=',True)
                                    ],
                                default = get_sh_smps_pro_field_ids,
                                )
   
    sh_smps_pro_attr_ids = fields.Many2many("product.attribute",
                                string = "Product Attributes",
                                related = "company_id.sh_smps_pro_attr_ids",
                                default = get_sh_smps_pro_attr_ids,                                         
                                )    
   

   
    
    
    
    
    