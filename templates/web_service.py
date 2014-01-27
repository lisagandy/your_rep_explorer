from werkzeug.wrappers import Request, Response
import simplejson
import cherrypy

import werkzeug
import sys
#sys.path.insert(0,'cherrypy.zip')
#import cherrypy
#from cherrypy import expose

@Request.application
def yourview(request):
   obj = 'stuff'
   json = simplejson.dumps('stuff')
   return HttpResponse(json, mimetype='application/json')

# class Service:
# 
#     @expose
#     def index(self):
#         return 'Hello World'
# 
# cherrypy.quickstart(Service())



# @Request.application
# def application(request):
#     return Response(simplejson.dumps({'stuff':'stuff1','stuff2':'stuff'}))
# 
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, yourview)