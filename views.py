from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response 
import re
from perspectives_server.utilities.client_common import verify_notary_signature, notary_reply_as_text,fetch_notary_xml, parse_http_notary_list
from perspectives_server.utilities.generate_svg import get_svg_graph
import time
import traceback 


host_regex = re.compile('^(([0-9]+\.[0-9]+\.[0-9]+\.[0-9]$)|(([a-zA-Z0-9\-]+\.)+([a-zA-Z\-]+)))$')

abs_http_notary_list_file = "/home/ubuntu/http_notary_list.txt"

def get_results(sid): 
	notary_server_list = parse_http_notary_list(abs_http_notary_list_file)		
	got_at_least_one = False
	for s in notary_server_list: 
		try:
			s["results"] = None
			nserver = s["host"].split(":")[0]
			nport = s["host"].split(":")[1]
			code, xml_text = fetch_notary_xml(nserver,int(nport), sid)
			if code == 200 and verify_notary_signature(sid, xml_text, s["public_key"]):
				# results are good
				s["results"] = xml_text
				got_at_least_one = True
			else: 
				print "invalid response from notary '%s'" % s["host"]	
		except Exception, e:
			print "Exception contacting notary server: '%s'" % s["host"] 
			traceback.print_exc(e)
	if not got_at_least_one: 
		return None
	return notary_server_list 

def notary_svg(request, host, port, duration): 
	if not host_regex.match(host): 	
		return HttpResponseBadRequest("Invalid host '%s'" % host)
	try: 
		duration_i = int(duration)
		port_i = int(port) 
		assert (port_i > 0 and port_i <= 65535)
		
	except: 
		return HttpResponseBadRequest("Invalid port '%s' or duration '%s'" \
						% (port, duration))
	sid = str(host + ":" + port + ",2") 
	notary_server_list = get_results(sid)
	if notary_server_list is None: 
		return HttpResponseNotFound("no notary replies") 
	svg =  get_svg_graph(sid, notary_server_list, duration_i, time.time())
	return HttpResponse(svg, mimetype='image/svg+xml')

def notary_query(request): 
	host = request.GET.get('host','www.cs.cmu.edu')
	if not host_regex.match(host): 	
		return HttpResponseBadRequest("Invalid host '%s'" % host)
	try: 
		port = int(request.GET.get('port', "443"))
		assert (port > 0 and port <= 65535)
	except:
		return HttpResponseBadRequest("Invalid port '%s'" % port)
	sid = str(host + ":" + str(port) + ",2") 
	notary_server_list = get_results(sid) 
	
	
	if notary_server_list is not None: 
		full_text = ""
		for s in notary_server_list:
			full_text += "\n" + (50 * "*") + "\n"
			if s["results"] is None:
       				full_text += "<No notary results>"
			else:
				full_text += notary_reply_as_text(s["results"])

	return render_to_response('notary_query.html', locals())

