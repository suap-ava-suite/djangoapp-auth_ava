# Configuration file for Sphinx documentation of django-auth-ava
import os
import sys

# Ensure package src is in Python path
sys.path.insert(0, os.path.abspath("../src"))

import django_docs_theme

project = "django-auth-ava"
copyright = "2026, Kelson da Costa Medeiros"
author = "Kelson da Costa Medeiros"
release = "0.1.0"
language = "pt_BR"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    "django_docs_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "django_docs_theme"
html_theme_path = [django_docs_theme.get_html_theme_path()]

html_theme_options = {
    "project_name": "django-auth-ava",
    "tagline": "Modelos concretos e normalizados para autenticação SUAP no ecossistema AVA",
    "github_url": "https://github.com/suap-ava-suite/djangoapp-auth_ava",
    "github_repo": "suap-ava-suite/djangoapp-auth_ava",
    "github_version": "main",
    "doc_path": "docs/",
    "show_edit_on_github": True,
    "navigation_links": (
        "Início|index.html, Instalação|installation.html, Configuração|configuration.html, "
        "Modelos|models.html, Fetchers|fetchers.html, Admin|admin.html, Desenvolvimento|development.html, "
        "GitHub|https://github.com/suap-ava-suite/djangoapp-auth_ava"
    ),
}

html_static_path = ["_static"]
