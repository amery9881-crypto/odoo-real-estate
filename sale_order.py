from odoo import api, models,fields


class SaleOrder(models.Model):
    _inherit="sale.order"


    property_id=fields.Many2one('property')
    owner_id=fields.Many2one('owner', related='property_id.owner_id', readonly=True)
    @api.onchange('property_id')
    def _onchange_property_id(self): 
        if self.property_id:
            product=self.property_id.product_id
            if not product:
                product= self.env['product.product'].create({
                    'name':self.property_id.name,
                    'list_price':self.property_id.selling_price or 0.0,
                    'type':'service'
                })
                self.property_id.product_id = product.id

            self.order_line = [(5, 0, 0)]
            self.order_line = [(0, 0, {
                'product_id':self.property_id.product_id.id,
                'name': self.property_id.name,
                'postcode':self.property_id.postcode,
                'price_unit': self.property_id.selling_price,
                'product_uom_qty': 1.0,
            })]

    @api.model
    def create(self, vals): 
        res = super(SaleOrder, self).create(vals)
        if res.property_id and res.property_id.state == 'draft':
            res.property_id.state = 'pending'
        return res
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.property_id and order.partner_id:
                order.property_id.state = 'pending'
                order.property_id.partner_id = order.partner_id.id

        return res

    def _prepare_invoice(self):
        invoice_vals=super (SaleOrder,self)._prepare_invoice()
        invoice_vals['property_id'] = self.property_id.id if self.property_id else False
        return invoice_vals




class SaleOrderLine(models.Model):
    _inherit="sale.order.line"

    postcode=fields.Char()