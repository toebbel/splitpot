<%! import cherrypy %>
<%! from utils.Auth import getCurrentUserName %>
<div class="navbar navbar-inverse navbar-fixed-top">
  <div class="navbar-inner">
    <div class="container">
      <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
      <span class="icon-bar"></span>
      </a>
      <a class="brand" href="#">Splitpot</a>
      <div class="nav-collapse collapse">
        <ul class="nav">
        % if getCurrentUserName() != '':
        <li><a href="${cherrypy.url('/list')}">List</a></li>
        <li><a href="${cherrypy.url('/add')}">Add</a></li>
        <li><a href="${cherrypy.url('/user/logout')}">Logout</a></li>
        % else:
        <li><a href="${cherrypy.url('/about')}">About</a></li>
        <li><a href="${cherrypy.url('/user/login')}">Login</a></li>
        % endif
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
</div>
