```
-----------------------------------------------------------------------------                                                           

 ██╗    ██╗ ██╗  ██╗  █████╗  ██╗  ██╗ ███████╗ ██████╗  ██████╗ ██╗   ██╗
 ██║    ██║ ██║  ██║ ██╔══██╗ ██║ ██╔╝ ██╔════╝ ██╔══██╗ ██╔══██╗╚██╗ ██╔╝
 ██║ █╗ ██║ ███████║ ███████║ █████╔╝  █████╗   ██████╔╝ ██████╔╝ ╚████╔╝ 
 ██║███╗██║ ██╔══██║ ██╔══██║ ██╔═██╗  ██╔══╝   ██╔══██╗ ██╔═══╝   ╚██╔╝  
 ╚███╔███╔╝ ██║  ██║ ██║  ██║ ██║  ██╗ ███████╗ ██║  ██║ ██║        ██║   
  ╚══╝╚══╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝        ╚═╝   
       
   a Python library to create dynamic HTML content and web applications

               Copyright (C) 2023-2024 Brigitte Bigi, CNRS, 
         Laboratoire Parole et Langage, Aix-en-Provence, France
         
-----------------------------------------------------------------------------                                                              
```

-----------------------------------------------------------------------------

 ██╗    ██╗ ██╗  ██╗  █████╗  ██╗  ██╗ ███████╗ ██████╗  ██████╗ ██╗   ██╗
 ██║    ██║ ██║  ██║ ██╔══██╗ ██║ ██╔╝ ██╔════╝ ██╔══██╗ ██╔══██╗╚██╗ ██╔╝
 ██║ █╗ ██║ ███████║ ███████║ █████╔╝  █████╗   ██████╔╝ ██████╔╝ ╚████╔╝ 
 ██║███╗██║ ██╔══██║ ██╔══██║ ██╔═██╗  ██╔══╝   ██╔══██╗ ██╔═══╝   ╚██╔╝  
 ╚███╔███╔╝ ██║  ██║ ██║  ██║ ██║  ██╗ ███████╗ ██║  ██║ ██║        ██║   
  ╚══╝╚══╝  ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝        ╚═╝   

   a Python library to create dynamic HTML content and web applications

               Copyright (C) 2023-2025 Brigitte Bigi, CNRS
         Laboratoire Parole et Langage, Aix-en-Provence, France

-----------------------------------------------------------------------------

# WebApp package

## Scope

The `webapp` package implements the **application layer** of WhakerPy.

It is responsible for:
- loading and validating web application configuration
- launching a local HTTP server
- connecting applications to the HTTPD engine
- providing a clean interface between **applications** and **HTTP transport**

This package **does not** implement HTTP mechanics or security logic.
Those belong to `httpd`.


## Design principles

### 1. Clear separation from HTTPD

| Concern | Package |
|------|---------|
| HTTP protocol, handlers, policies | `httpd` |
| Application configuration and launch | `webapp` |
| UI / HTML generation | `response` (external) |

`webapp` glues **applications** to the **HTTP engine**.


### 2. One application = one configuration

Each web application is described by:
- a JSON configuration file
- parsed once into a `WebSiteData` object

That object becomes the **single source of truth** for:
- page tree
- static paths
- blacklist rules
- signed URL rules

No duplicated parsing.


### 3. Same application, two execution modes

The same application can run:
- locally (built-in HTTP server)
- in production (uWSGI / WSGI)

`webapp` ensures:
- identical configuration
- identical policy behavior
- no application-side branching


## Main modules and roles

### WebSiteData

Role:
- configuration loader and validator

Main class:
- `WebSiteData`

Responsibilities:
- parse JSON configuration
- expose structured attributes (pages, static paths, blacklist, signed_url)
- create the dynamic page tree

It does **not**:
- serve HTTP
- apply policies
- generate responses

It is a **data container**, not a controller.

### WebSiteApplication

Role:
- local application launcher

Main class:
- `WebSiteApplication`

Responsibilities:
- instantiate the HTTP server (`BaseHTTPDServer`)
- pass configuration to the server
- start / stop the local server
- compute client URL

This is the **only place** where:
- server lifecycle is managed
- configuration is injected into the server

It does **not**:
- handle requests
- implement policies
- generate HTML


### WebSiteResponse

Role:
- base interface between applications and the server

Responsibilities:
- define how an application exposes pages
- map page names to response builders
- provide default behaviors

This module defines the **contract** an application must satisfy
to be served by WhakerPy.

It does **not**:
- know routing rules
- know security policies
- access configuration directly


### WSGIApplication

Role:
- WSGI entry point for production deployment

Main class:
- `WSGIApplication`

Responsibilities:
- adapt WhakerPy to the WSGI interface
- forward requests to the same HTTPD logic
- apply the same policies as the local server

Guarantees:
- identical behavior local / production
- no duplicated logic


## Extensibility

This package is the right place to add:
- new application launchers
- alternative configuration sources
- new application descriptors

Without touching:
- HTTP handlers
- security policies
- application code


## Summary

- `webapp` is the **application orchestration layer**
- it loads configuration once
- it launches applications consistently
- it bridges applications and HTTPD cleanly
- it keeps application code independent of transport details

This package defines **how an application becomes a website**.





