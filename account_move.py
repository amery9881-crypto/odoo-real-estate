from odoo import models,fields


class AccountMove(models.Model):
    _inherit="account.move"



    property_id = fields.Many2one('property' ,readonly=True)
    owner_id= fields.Many2one('owner',related='property_id.owner_id',store=True,readonly=True)

    def action_post(self):
        res= super(AccountMove, self).action_post()
        for move in self:
            if move.property_id and move.move_type == 'out_invoice':
                move.property_id.state='sold'
        return res

    def write(self, vals):
        res= super(AccountMove, self).write(vals)
        for move in self:
            if move.property_id and move.move_type == 'out_invoice' and move.payment_state ==('paid','in_payment'):
                move.property_id.state='sold'
        return res       


    def button_draft(self): 
        res = super(AccountMove, self).button_draft() 
        for move in self: 
            if move.property_id: 
                move.property_id.state = 'draft' 
        return res


    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        for move in self:
            if move.property_id:
                move.property_id.state = 'draft'
        return res

    class AccountMoveLine(models.Model):
        _inherit="account.move.line"

        postcode=fields.Char(related='move_id.property_id.postcode', store=True,readonly=True)
        


