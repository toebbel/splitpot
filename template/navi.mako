<%! import cherrypy %>
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
        <li><a href="${cherrypy.url('/list')}">List</a></li>
        <li><a href="${cherrypy.url('/add')}">Add</a></li>
        <li><a href="${cherrypy.url('/about')}">About</a></li>
        </ul>
      </div><!--/.nav-collapse -->
    </div>
  </div>
</div>
