# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
import glob
import shutil
import inspect
# import m2r
import builtins

import pt_lightning_sphinx_theme

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_ROOT = os.path.join(PATH_HERE, '..', '..')
sys.path.insert(0, os.path.abspath(PATH_ROOT))

builtins.__LIGHTNING_BOLT_SETUP__ = True

import pytorch_lightning_bolts  # noqa: E402

# -- Project information -----------------------------------------------------

project = 'PyTorchLightning-Bolts'
copyright = pytorch_lightning_bolts.__copyright__
author = pytorch_lightning_bolts.__author__

# The short X.Y version
version = pytorch_lightning_bolts.__version__
# The full version, including alpha/beta/rc tags
release = pytorch_lightning_bolts.__version__

# Options for the linkcode extension
# ----------------------------------
github_user = 'PyTorchLightning'
github_repo = project


# -- Project documents -------------------------------------------------------

# export the documentation
with open('intro.rst', 'w') as fp:
    fp.write(pytorch_lightning_bolts.__long_doc__)

# export the READme
with open(os.path.join(PATH_ROOT, 'README.md'), 'r') as fp:
    readme = fp.read()
for dir_name in (os.path.basename(p) for p in glob.glob(os.path.join(PATH_ROOT, '*')) if os.path.isdir(p)):
    readme = readme.replace('](%s/' % dir_name, '](%s/%s/' % (PATH_ROOT, dir_name))
with open('readme.md', 'w') as fp:
    fp.write(readme)

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.

needs_sphinx = '2.2'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    # 'sphinxcontrib.mockautodoc',  # raises error: directive 'automodule' is already registered ...
    # 'sphinxcontrib.fulltoc',  # breaks pytorch-theme with unexpected kw argument 'titles_only'
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.linkcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'recommonmark',
    'sphinx.ext.autosectionlabel',
    # 'm2r',
    'nbsphinx',
    'sphinx_autodoc_typehints',
    'sphinx_paramlinks',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# https://berkeley-stat159-f17.github.io/stat159-f17/lectures/14-sphinx..html#conf.py-(cont.)
# https://stackoverflow.com/questions/38526888/embed-ipython-notebook-in-sphinx-document
# I execute the notebooks manually in advance. If notebooks test the code,
# they should be run at build time.
nbsphinx_execute = 'never'
nbsphinx_allow_errors = True
nbsphinx_requirejs_path = ''

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
# source_suffix = ['.rst', '.md', '.ipynb']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
    '.ipynb': 'nbsphinx',
}

# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'pytorch_lightning_bolts.rst',
    'modules.rst',
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'pt_lightning_sphinx_theme'
html_theme_path = [pt_lightning_sphinx_theme.get_html_theme_path()]

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_theme_options = {
    'pytorch_project': pytorch_lightning_bolts.__homepage__,
    'canonical_url': pytorch_lightning_bolts.__homepage__,
    'collapse_navigation': False,
    'display_version': True,
    'logo_only': False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_templates']  # '_static'

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project + '-doc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',

    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, project + '.tex', project + ' Documentation', author, 'manual'),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, project, project + ' Documentation', [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, project, project + ' Documentation', author, project,
     'The lightweight PyTorch wrapper for ML researchers. Scale your models. Write less boilerplate.',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# https://github.com/rtfd/readthedocs.org/issues/1139
# I use sphinx-apidoc to auto-generate API documentation for my project.
# Right now I have to commit these auto-generated files to my repository
# so that RTD can build them into HTML docs. It'd be cool if RTD could run
# sphinx-apidoc for me, since it's easy to forget to regen API docs
# and commit them to my repo after making changes to my code.

PACKAGES = [
    pytorch_lightning_bolts.__name__,
]


def run_apidoc(_):
    for pkg in PACKAGES:
        argv = ['-e', '-o', PATH_HERE, os.path.join(PATH_HERE, PATH_ROOT, pkg),
                '**/test_*', '--force', '--private', '--module-first']
        # Sphinx 1.7+
        from sphinx.ext import apidoc
        apidoc.main(argv)


def setup(app):
    app.connect('builder-inited', run_apidoc)


# copy all notebooks to local folder
path_nbs = os.path.join(PATH_HERE, 'notebooks')
if not os.path.isdir(path_nbs):
    os.mkdir(path_nbs)
for path_ipynb in glob.glob(os.path.join(PATH_ROOT, 'notebooks', '*.ipynb')):
    path_ipynb2 = os.path.join(path_nbs, os.path.basename(path_ipynb))
    shutil.copy(path_ipynb, path_ipynb2)

# Ignoring Third-party packages
# https://stackoverflow.com/questions/15889621/sphinx-how-to-exclude-imports-in-automodule

MOCK_REQUIRE_PACKAGES = []
with open(os.path.join(PATH_ROOT, 'requirements.txt'), 'r') as fp:
    for ln in fp.readlines():
        found = [ln.index(ch) for ch in list(',=<>#') if ch in ln]
        pkg = ln[:min(found)] if found else ln
        if pkg.rstrip():
            MOCK_REQUIRE_PACKAGES.append(pkg.rstrip())

# TODO: better parse from package since the import name and package name may differ
MOCK_MANUAL_PACKAGES = [
    'torch',
    'pytorch_lightning',
    'torchvision',
]
autodoc_mock_imports = MOCK_REQUIRE_PACKAGES + MOCK_MANUAL_PACKAGES
# for mod_name in MOCK_REQUIRE_PACKAGES:
#     sys.modules[mod_name] = mock.Mock()


# Resolve function
# This function is used to populate the (source) links in the API
def linkcode_resolve(domain, info):
    def find_source():
        # try to find the file and line number, based on code from numpy:
        # https://github.com/numpy/numpy/blob/master/doc/source/conf.py#L286
        obj = sys.modules[info['module']]
        for part in info['fullname'].split('.'):
            obj = getattr(obj, part)
        fname = inspect.getsourcefile(obj)
        # https://github.com/rtfd/readthedocs.org/issues/5735
        if any([s in fname for s in ('readthedocs', 'rtfd', 'checkouts')]):
            # /home/docs/checkouts/readthedocs.org/user_builds/pytorch_lightning/checkouts/
            #  devel/pytorch_lightning/utilities/cls_experiment.py#L26-L176
            path_top = os.path.abspath(os.path.join('..', '..', '..'))
            fname = os.path.relpath(fname, start=path_top)
        else:
            # Local build, imitate master
            fname = 'master/' + os.path.relpath(fname, start=os.path.abspath('..'))
        source, lineno = inspect.getsourcelines(obj)
        return fname, lineno, lineno + len(source) - 1

    if domain != 'py' or not info['module']:
        return None
    try:
        filename = '%s#L%d-L%d' % find_source()
    except Exception:
        filename = info['module'].replace('.', '/') + '.py'
    # import subprocess
    # tag = subprocess.Popen(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE,
    #                        universal_newlines=True).communicate()[0][:-1]
    branch = filename.split('/')[0]
    # do mapping from latest tags to master
    branch = {'latest': 'master', 'stable': 'master'}.get(branch, branch)
    filename = '/'.join([branch] + filename.split('/')[1:])
    return "https://github.com/%s/%s/blob/%s" \
           % (github_user, github_repo, filename)


autodoc_member_order = 'groupwise'
autoclass_content = 'both'
# the options are fixed and will be soon in release,
#  see https://github.com/sphinx-doc/sphinx/issues/5459
autodoc_default_options = {
    'members': None,
    'methods': None,
    # 'attributes': None,
    'special-members': '__call__',
    'exclude-members': '_abc_impl',
    'show-inheritance': True,
    'private-members': True,
    'noindex': True,
}

# Sphinx will add “permalinks” for each heading and description environment as paragraph signs that
#  become visible when the mouse hovers over them.
# This value determines the text for the permalink; it defaults to "¶". Set it to None or the empty
#  string to disable permalinks.
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_add_permalinks
html_add_permalinks = "¶"

# True to prefix each section label with the name of the document it is in, followed by a colon.
#  For example, index:Introduction for a section called Introduction that appears in document index.rst.
#  Useful for avoiding ambiguity when the same section heading appears in different documents.
# http://www.sphinx-doc.org/en/master/usage/extensions/autosectionlabel.html
autosectionlabel_prefix_document = True
