# sphinx configuration

extensions = ["sphinx.ext.napoleon"]
html_theme = "alabaster"
html_static_path = ["source/frontend_client_docs"]
exclude_patterns = ["source/frontend_client_docs/**"]
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
project = "mex-editor-ng"
templates_path = ["."]
