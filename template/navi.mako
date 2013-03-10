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
      <a class="brand" href="${cherrypy.url('/')}">Splitpot</a>
      <div class="nav-collapse">
        <ul class="nav">
        % if getCurrentUserName() != '':
        <li><a href="${cherrypy.url('/list')}">List</a></li>
        <li><a href="${cherrypy.url('/add')}">Add</a></li>
        <!-- <li><a href="${cherrypy.url('/user/logout')}">Logout</a></li> -->
        <li>
            <div class="btn-group">
                <a class="btn btn-primary" href="#"><i class="icon-user icon-white"></i> User</a>
                <a class="btn btn-primary dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
                <ul class="dropdown-menu">
                    <li><a href="${cherrypy.url('/merge')}"><i class="icon-resize-small"></i> Merge</a></li>
                    <li><a href="${cherrypy.url('/alias')}"><i class="icon-plus"></i> Add Alias</a></li>
                    <li><a href="${cherrypy.url('/user/forgot')}"><i class="icon-pencil"></i> Change Password</a></li>
                    <li class="divider"></li>
                    <li><a href="${cherrypy.url('/user/logout')}"><i class="icon-off"></i> Logout</a></li>
                </ul>
            </div>
        </li>
        % else:
        <li><a href="${cherrypy.url('/about')}">About</a></li>
        <li><a href="${cherrypy.url('/user/login')}">Login</a></li>
        % endif
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
</div>
