import json
from urllib.parse import parse_qs
from odoo import http
from odoo.http import request
import math


def valid_response(data,status=200,pagination_info=None):
    response_body={
        'message':"successful",
        'data':data,
        'pagination_info':pagination_info

    }
    return request.make_json_response(response_body,status=status)

def invalid_response(error,status):
    response_body={
        'error':error
    }
    return request.make_json_response(response_body,status=status)


class PropertyApi(http.Controller):

    # @http.route("/v1/property", methods=["POST"], type="http",auth="none",csrf=False)
    
    # def post_property(self):
    #     print("INSIDE post_property")
    #     args = request.httprequest.data.decode()
    #     vals= json.loads(args)
    #     if not vals.get('name') or not vals.get ('postcode'):
    #         return request.make_json_response({
    #             "message": "recuied",
    #           },status=400)
    #     try:
    #         res= request.env['property'].sudo().create(vals)
    #         if res:
    #           return request.make_json_response({
    #             "message": "proprety hass been susseful",
    #             "id":res.id,
    #             "name":res.name,

    #           },status=201)
    #     except Exception as error:
    #         return request.make_json_response({
    #             "message": error

    #           },status=400)
        
    @http.route("/v1/property", methods=["POST"], type="http",auth="none",csrf=False)
            
    def post_property(self):
                print("INSIDE post_property")
                args = request.httprequest.data.decode()
                vals= json.loads(args)
                if not vals.get('name') or not vals.get ('postcode'):
                    return request.make_json_response({
                        "message": "recuied",
                      },status=400)
                try:
                    cr= request.env.cr
                    columns=','.join(vals.keys())
                    values=','.join(['%s']*len(vals))
                    query= f"""INSERT INTO property ({columns} ) VALUES ({values}) RETURNING id, name, postcode"""
                    cr.execute(query, tuple(vals.values()))
                    res=cr.fetchone()
                    print(res)
                    if res:
                      return request.make_json_response({
                        "message": "proprety hass been susseful",
                        "id":res[0],
                        "name":res[1],
                        "postcode":res[2],
        
                      },status=201)
                except Exception as error:
                    return request.make_json_response({
                        "message": error
        
                      },status=400)
        


    @http.route("/v1/property", methods=["POST"], type="json",auth="none",csrf=False)

    def post_property_json(self):
        args = request.httprequest.data.decode()
        vals= json.loads(args)
        res= request.env['property'].sudo().create(vals)
        if res:
            return{
                "message": "proprety hass been susseful"
            }

        
    @http.route("/v1/property/<int:property_id>", methods=["PUT"], type="http",auth="none",csrf=False)
    
    def update_property(self, property_id):
        try:
            property_id=request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return request.make_json_response({
                    "message": "Id does not found",
                        
                     },status=400)
                    

            args = request.httprequest.data.decode()
            vals= json.loads(args)
            print(vals)
            property_id.write(vals)
            return request.make_json_response({
                "message": "proprety hass been susseful",
                "id":property_id.id,
                "name":property_id.name,

              },status=201)
        except Exception as error:
           return request.make_json_response({
                "error": error
        
            },status=400)



    @http.route("/v1/property/<int:property_id>", methods=["GET"], type="http",auth="none",csrf=False)

    def get_property(self,property_id):
        try:
            property_id=request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
                return invalid_response("id does not exite!",status=400)
            return valid_response({
                "id":property_id.id,
                "name":property_id.name,
                "ref":property_id.ref,
                "description":property_id.description,
                "postcode":property_id.postcode,
                "bedrooms":property_id.bedrooms

              },status=201)
        except Exception as error:
            return request.make_json_response({
                "error": error
        
           },status=400)
        


    @http.route("/v1/property/<int:property_id>", methods=["DELETE"], type="http",auth="none",csrf=False)

    def delete_property(self,property_id):
        try:
            property_id=request.env['property'].sudo().search([('id', '=', property_id)])
            if not property_id:
               return request.make_json_response({
                    "error": "id does not exite!"
                                    
                },status=400)
            property_id.unlink()
            return request.make_json_response({
                "message":"property has been deleted successfuly"
            
            },status=201)
        except Exception as error:
            return request.make_json_response({
                "error": "error"
        
           },status=400)


    @http.route("/v1/properties/", methods=["GET"], type="http",auth="none",csrf=False)
    
    def get_property_list(self):
            try:
                params=parse_qs(request.httprequest.query_string.decode('utf-8'))
                property_domain= []
                page=offset= None
                limit=5
                if params.get('limit'):
                    limit=int(params.get('limit')[0])
                if params.get('page'):
                    page=int(params.get('page')[0])
                if page:
                    offset=(page*limit)-limit
                if params.get('state'):
                    property_domain +=[('state', '=', params.get('state')[0])]
                property_ids=request.env['property'].sudo().search(property_domain,offset=offset,limit=limit,order='id desc')
                property_count=request.env['property'].sudo().search_count(property_domain)
                if not property_ids:
                    return request.make_json_response({
                        "error": "There are not records!"
                            
                    },status=400)
                return valid_response([{
                    "id":property_id.id,
                    "name":property_id.name,
                    "ref":property_id.ref,
                    "description":property_id.description,
                    "postcode":property_id.postcode,
                    "bedrooms":property_id.bedrooms
    
                  }for property_id in property_ids],
                  pagination_info={
                      'page':page if page else 1,
                      'limit':limit,
                      'pages':math.ceil(property_count/limit)if limit else 1,
                      'count':property_count
                  },status=201)
            except Exception as error:
                return request.make_json_response({
                    "error": error
            
               },status=400)

        


