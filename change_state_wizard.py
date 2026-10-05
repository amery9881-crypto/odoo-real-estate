from odoo import fields,models


class ChangeState(models.TransientModel):
    _name='change.state'
    
    property_id=fields.Many2one('property')
    state=fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
    ],default='draft')

    reason=fields.Char()

    def action_confirm(self):
        self.ensure_one()
        if self.property_id:
            self.property_id.with_context(history_reason=self.reason).write({
                'state': self.state
            })
        return {'type': 'ir.actions.act_window_close'}


        


    