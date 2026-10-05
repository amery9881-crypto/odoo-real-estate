from odoo import models,fields,api
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta
import requests


class Property(models.Model):
    _name="property"
    _description="Property"

    _inherit=['mail.thread','mail.activity.mixin']

    name = fields.Char(required=1, default="New", size=20,)
    ref = fields.Char(default='New', readonly=1)
    description = fields.Text(tracking=True)
    postcode = fields.Char(required=1)
    date_availab= fields.Date(tracking=True)
    expeceted_price= fields.Float(digits=(0, 0))
    selling_price= fields.Float(digits=(0, 0))
    exceptd_selling_date=fields.Date(tracking=True)
    is_late=fields.Boolean(compute='_compute_is_late')
    diff=fields.Float(compute='_compute_diff',digits=(0, 0),store=True, readonly=False)
    bedrooms= fields.Integer()
    living_area= fields.Integer()
    facades= fields.Integer()
    garage=fields.Boolean()
    garden= fields.Boolean(groups="app_one.property_manager_group")
    garden_area=fields.Integer()
    create_time=fields.Datetime(default=fields.Datetime.now())
    next_time=fields.Datetime(compute='_compute_next_time',store=True)

    garden_orientation=fields.Selection([
        ('north','North'),
        ('south','South'),
        ('east','East'),
        ('west','West'),

    ],  default="north", string='Garden_Orientation')

    owner_id=fields.Many2one('owner')
    tag_ids=fields.Many2many('tag')
    owner_address=fields.Char(related='owner_id.address', readonly=False)
    owner_phone=fields.Char(related='owner_id.phone', readonly=False)
    active=fields.Boolean(default=True)
    product_id=fields.Many2one('product.product', copy=False)
    sale_order_id = fields.Many2one('sale.order',copy=False)
    partner_id=fields.Many2one('res.partner', store=True)




    state=fields.Selection([
        ('draft','Draft'),
        ('pending','Pending'),
        ('sold','Sold'),
        ('closed','Closed'),
    ],default="draft")

    @api.model
    def create(self, vals):
        product_vals = {
           'name': vals.get('name','عقار جديد'),
           'list_price': vals.get('selling_price', 0.0),
           'type': 'service',
           'purchase_ok': True,
        }
        product = self.env['product.product'].create(product_vals)
        vals['product_id'] = product.id
        property_record = super(Property, self).create(vals)
    
        return property_record

    def write(self, vals): 
        res = super(Property, self).write(vals) 
        for rec in self: 
            if rec.product_id: 
                product_vals = {} 
                if 'name' in vals: 
                    product_vals['name'] = vals['name'] 
                if 'selling_price' in vals: 
                   product_vals['list_price'] = vals['selling_price'] 
                if product_vals: 
                    rec.product_id.write(product_vals) 
        return res

    _sql_constraints =[
        ('unique_name', 'unique(name)', 'this name is erist')
    ]

    line_ids=fields.One2many('property.line','property_id')


    @api.depends('expeceted_price','selling_price')
    def _compute_diff(self):
        for rec in self:
            rec.diff= rec.selling_price - rec.expeceted_price 

    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time=rec.create_time + timedelta(hours=6)
            else:
                rec.next_time=False



    



    @api.onchange('expeceted_price','selling_price')
    def _onchange_expeceted_price_selling_price(self):
        for rec in self:
            if rec.expeceted_price <0 or rec.selling_price <0:
              return{
                'warning':{
                    'title':'اكتب الرقم زي الناس 🤬',
                    'message':'negative value.',
                }
            }
        print("onchange")
    @api.constrains('expeceted_price','selling_price')
    def _check_expec_selling_greater_zero(self):
        for rec in self:
            if rec.expeceted_price < 0 or rec.selling_price <0:
                raise ValidationError("عفوا ! لا يمكن ان يكون السعر بالسالب")
            

    def action_draft(self):
        for rec in self:
            rec.state='draft'

    def action_pending(self):
            for rec in self:
                rec.state='pending'


    def action_sold(self):
            for rec in self:
                rec.state='sold'
    

    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed', reason= "Closed by button")
            rec.state='closed'


    @api.depends('exceptd_selling_date','state')
    def _compute_is_late(self):
        for rec in self:
            if rec.state == 'draft' and rec.exceptd_selling_date and rec.exceptd_selling_date < fields.date.today():
                rec.is_late = True
            else:
                rec.is_late = False

    def _check_exceptd_selling_date(self): 
       property_ids = self.search([]) 
       template = self.env.ref('app_one.email_template_property', raise_if_not_found=False)
       for rec in property_ids:
          if rec.state == 'draft' and rec.exceptd_selling_date and rec.exceptd_selling_date < fields.date.today():
              if template and rec.partner_id and rec.partner_id.email:
                template.send_mail(rec.id, force_send=True)
                print(f"--> Email Sent Successfully to: {rec.partner_id.email}")
              else:
                print("--> WARNING: Partner or Email is missing!")

    def action(self):
       print(self.env['property'].search(['|',('name','=','property2'),('postcode','!=','ddewd2')]))

    @api.model_create_multi
    def create(self, vals):
        res=super(Property,self).create(vals)
        if res.ref =='New':
            res.ref=self.env['ir.sequence'].next_by_code('property_seq')
        return res

    def action_send_property_email(self): 
        self.ensure_one()

           
        if not self.partner_id or not self.partner_id.email:
           raise UserError("لا يوجد عميل مرتبط بهذه الشقة أو العميل ليس لديه بريد إلكتروني صالح!")

        template_id = self.env.ref('app_one.email_template_property', raise_if_not_found=False)
        if not template_id:
           raise UserError("قالب الإيميل غير موجود.")

        return {
         'type': 'ir.actions.act_window',
         'name': 'Send by Email',
         'res_model': 'mail.compose.message',
         'view_mode': 'form',
         'target': 'new',
         'context': {
            'default_model': 'property',
            'default_res_ids': [self.id],
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'default_partner_ids': [(4, self.partner_id.id)],
            'force_email': True,
        }
    }

       
    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms ==0:
                raise ValidationError("please add valid number of bedrooms")

    def action_open_change_state_wizard(self):
            action= self.env['ir.actions.actions']._for_xml_id('app_one.change_state_action')
            action['context']={'default_property_id': self.id}
            return action
    

    def write(self, vals):
        old_states = {rec.id: rec.state for rec in self}
   
        res = super(Property, self).write(vals)
        if 'state' in vals:
          for rec in self:
            old_state = old_states.get(rec.id)
            new_state = vals.get('state')
    
            if old_state != new_state:
                reason = self.env.context.get('history_reason', 'Updated automatically')
                rec.create_history_record(
                    old_state=old_state,
                    new_state=new_state,
                    reason=reason
                )
        return res


    def create_history_record(self,old_state,new_state,reason):
        for rec in self:
            rec.env['property.history'].create({
                'user_id':rec.env.uid,
                'property_id':rec.id,
                'old_state':old_state,
                'new_state':new_state,
                'reason'  :reason or "",
                'is_active' :rec.active,
                'line_ids':[(0, 0, {'description':line.description, 'area':line.area}) for line in rec.line_ids],
            })

    def action_related_owner(self):
        action= self.env['ir.actions.actions']._for_xml_id('app_one.owner_action')
        view_id = self.env.ref('app_one.owner_view_form').id
        action['res_id']= self.owner_id.id
        action['views']= [[view_id, 'form']]
        return action

    def get_properties(self):
        payload= dict()
        try:
            response=requests.get('http://127.0.0.1:8069/v1/properties',data=payload)
            if response.status_code==201:
                print(response.json())
            else:
                print("error")
        except Exception as error:
            raise ValidationError(str(error))

 
    def property_xlsx_report(self):
        return {
            'type':'ir.actions.act_url',
            'url':f'/property/excel/report/{self.env.context.get("active_ids")}',
            'target':'new'
        }


    def _get_report_base_filename(self):
        self.ensure_one()
        return f'Property - {self.name}'





class PropertyLine(models.Model):
    _name="property.line"


    area=fields.Float()
    description=fields.Char()
    property_id=fields.Many2one('property')


