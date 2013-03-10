<%! import cherrypy %>
<meta encoding="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <title><%block name="title" /></title>

    <meta name="description" content="" />
    <link rel="stylesheet" href="${cherrypy.url('/asset/css/bootstrap.css')}" media="screen"/>
    <link rel="stylesheet" href="${cherrypy.url('/asset/css/custom.css')}" media="screen"/>
    <link rel="stylesheet" href="${cherrypy.url('/asset/css/datepicker.css')}" media="screen"/>
    
    <link rel="stylesheet" href="http://code.jquery.com/ui/1.9.2/themes/base/jquery-ui.css" type="text/css">
    <link href="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/css/bootstrap-combined.min.css" rel="stylesheet">
    <script src="http://code.jquery.com/jquery-1.8.3.js" type="text/javascript"></script>
    <script src="http://code.jquery.com/ui/1.9.2/jquery-ui.js" type="text/javascript"></script>
    <script src="//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.1/js/bootstrap.min.js"></script>
    <script src="${cherrypy.url('/asset/js/bootstrap-datepicker.js')}"></script>
    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
        background-color: #f5f5f5;
      }
      
      @media (max-width: 767px) {
          /* Remove any padding from the body */
          body {
            padding-top: 0;
          }
      }

      .form-signin {
        max-width: 300px;
        padding: 19px 29px 29px;
        margin: 0 auto 20px;
        background-color: #fff;
        border: 1px solid #e5e5e5;
        -webkit-border-radius: 5px;
           -moz-border-radius: 5px;
                border-radius: 5px;
        -webkit-box-shadow: 0 1px 2px rgba(0,0,0,.05);
           -moz-box-shadow: 0 1px 2px rgba(0,0,0,.05);
                box-shadow: 0 1px 2px rgba(0,0,0,.05);
      }

      .form-signin input[type="text"],
      .form-signin input[type="password"] {
        font-size: 16px;
        height: auto;
        margin-bottom: 15px;
        padding: 7px 9px;
      } 

      .navbar .brand,
      .nav-collapse {
        float:none;
        display:inline-block;
        *display:inline; /* ie7 fix */
        *zoom:1; /* hasLayout ie7 trigger */
        vertical-align: top;
      }
      .navbar-inner > .container { text-align:center; }

      @media (max-width: 970px) {
        .navbar .brand,
        .nav-collapse {
            display: block;
        }
      }

    </style>

    <link rel="shortcut icon" href="${cherrypy.url('/asset/ico/favicon.ico')}">
