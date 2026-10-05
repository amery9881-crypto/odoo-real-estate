from odoo import models,fields



class PropertyHistory(models.Model):
    _name="property.history"
    _description="Property History"

    user_id=fields.Many2one('res.users')
    property_id=fields.Many2one('property', context={'active_test':False})
    old_state=fields.Char()
    new_state=fields.Char()
    is_active= fields.Boolean(string='Active', default=True)
    reason=fields.Char()
    line_ids=fields.One2many('property.history.line','history_id')

class PropertyHistoryLine(models.Model):
    _name="property.history.line"


    area=fields.Float()
    description=fields.Char()
    history_id=fields.Many2one('property.history')

    