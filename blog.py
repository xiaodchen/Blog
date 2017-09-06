import random
import hashlib
import hmac
import os
import re
from string import letters
import urllib2
import json
import webapp2
import jinja2
import logging
import time 

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d): 
        json_txt = json.dumps(d)
        self.response.headers['Content-type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def initialize(self, *a, **kw): 
        webapp2.RequestHandler.initialize(self, *a, **kw)
        if self.request.url.endswith('.json'): 
            self.format = 'json'
        else: 
            self.format = 'html'

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, World!')

##### blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    def as_dict(self): 
        d = {'subject':self.subject, 
             'content':self.content,
             'created':self.created.strftime('%c'),
             'last_modified':self.last_modified.strftime('%c')}
        return d

class BlogFront(BlogHandler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        if self.format == 'html': 
            self.render('front.html', posts = posts)
        else: 
            self.render_json([p.as_dict() for p in posts])

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return
        if self.format == 'html': 
            self.render("permalink.html", post = post)
        else: 
            self.render_json(post.as_dict())

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/blog/?(?:.json)?', BlogFront),
                               ('/blog/([0-9]+)(?:.json)?', PostPage),
                               ('/blog/newpost', NewPost),
                               ],
                              debug=True)
