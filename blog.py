# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2, os, jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'template')
print '@@@@', template_dir
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
								autoescape = True)
class Blog(db.Model): 
	subject = db.StringProperty(required = True)
	blog = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)


class Handler(webapp2.RequestHandler): 
	def write(self, *a, **kw): 
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params): 
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw): 
		self.write(self.render_str(template, **kw))


class FrontPage(Handler): 
	def render_front(self): 
		blogs = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC')
		self.render('blog.html', blogs = blogs)

	def get(self): 
		self.render_front()

class PostPage(Handler): 
	def get(self, post_id):
		blog = Blog.get_by_id(int(post_id))
		self.render('newpost.html', blog = blog)

class MainPage(Handler): 
	def render_post(self, subject = '', blog = '', error = ''): 
		self.render('newblog.html', subject = subject, blog = blog, error = error)

	def get(self): 
		self.render_post()

	def post(self): 
		subject = self.request.get('subject')
		blog = self.request.get('content')
		if subject and blog: 
			b = Blog(subject = subject, blog = blog)
			b.put()
			post_id = b.key().id()
			print '@@@@', post_id 
			self.redirect('/blog/'+str(post_id))
		else: 
			error = 'Enter both subject and blog.'
			self.render_post(subject, blog, error)

app = webapp2.WSGIApplication([('/blog/newpost', MainPage),
							   ('/blog', FrontPage),
							   ('/blog/(\d+)', PostPage) 
							  ], debug = True)

 