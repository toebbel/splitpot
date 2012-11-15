<%! import cherrypy %>
<meta encoding="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <title><%block name="title" /></title>

    <meta name="description" content="" />
    <link rel="stylesheet" href="${cherrypy.url('/asset/css/bootstrap.css')}" media="screen"/>

    <style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }
    </style>
    <link rel="shortcut icon" href="${cherrypy.url('/asset/ico/favicon.ico')}">
