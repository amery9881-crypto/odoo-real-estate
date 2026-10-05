from odoo.tests.common import TransactionCase
from odoo import fields
class TestProperty(TransactionCase):

    def setUp(self,*args, **kwargs):
        super(TestProperty,self).setUp()

        self.property_01_record=self.env['property'].create({
            'ref':'PRT1000',
            'name':'Property 1000',
            'description':'Property 1000',
            'date_availab':fields.Date.today(),
            'bedrooms':5,
            'expeceted_price':1000,
            'postcode':'5555'

        })


    def test_01_property_values(self):
        property_id= self.property_01_record

        self.assertRecordValues(property_id,[{
            'ref':'PRT1000',
            'name':'Property 1000',
            'description':'Property 1000',
            'date_availab':fields.Date.today(),
            'bedrooms':5,
            'expeceted_price':1000,
            'postcode':'5555'



        }])
