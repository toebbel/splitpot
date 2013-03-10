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
      % if getCurrentUserName() != '':
      <div class="btn-group pull-right">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><i class="icon-user"></i> User <span class="caret"></span></a>
          <!-- if we should ever need two separate buttons
              <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"><span class="caret"></span></a>
          -->
          <ul class="dropdown-menu" data-no-collapse="true">
              <li style="text-align:left;"><a href="${cherrypy.url('/merge')}"><i class="icon-resize-small"></i> merge</a></li>
              <li style="text-align:left;"><a href="${cherrypy.url('/alias')}"><i class="icon-plus"></i> add alias</a></li>
              <li style="text-align:left;"><a href="${cherrypy.url('/user/forgot')}"><i class="icon-pencil"></i> change password</a></li>
              <li class="divider"></li>
              <li style="text-align:left;"><a href="${cherrypy.url('/user/logout')}"><i class="icon-off"></i> logout</a></li>
          </ul>
      </div>
      % endif
      <div class="nav-collapse">
        <ul class="nav">
            % if getCurrentUserName() != '':
                <li><a href="${cherrypy.url('/list')}">List</a></li>
                <li><a href="${cherrypy.url('/add')}">Add</a></li>
            % else:
                <li><a href="${cherrypy.url('/about')}">About</a></li>
                <li><a href="${cherrypy.url('/user/login')}">Login</a></li>
            % endif
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
</div>
