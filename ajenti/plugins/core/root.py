import re

import ajenti.ui as ui
from ajenti.com import *
from ajenti.app.api import ICategoryProvider, IEventDispatcher
from ajenti.app.helpers import CategoryPlugin
from ajenti.app.urlhandler import URLHandler, url, get_environment_vars

class RootDispatcher(URLHandler, Plugin):

    categories = Interface(ICategoryProvider)
    event_dispatchers = Interface(IEventDispatcher)

    def main_ui(self):
        templ = self.app.get_template('main.xml')
        h = ui.Html()

        cat_selected = self.app.session.get('cat_selected',0)

        cat = None
        v = ui.VContainer()
        for num, c in enumerate(self.categories):
            if num == cat_selected:
                v.vnode(ui.Category(c.category, id=str(num), selected='true'))
                cat = c
            else:
                v.vnode(ui.Category(c.category, id=str(num)))

        templ.appendChildInto('leftplaceholder', v)

        templ.appendChildInto('rightplaceholder', cat.get_ui())

        return templ

    @url('^/$')
    def process(self, req, start_response):
        templ = self.app.get_template('index.xml')

        main = self.main_ui()

        templ.appendChildInto('body', main.elements())

        return templ.render()

    @url('^/handle/category/click/\d+')
    def handle(self, req, start_response):
        match = re.match('^/handle/category/click/(\d+)', req['PATH_INFO'])
        if not match:
            return 'Error'

        cat = match.group(1)
        self.app.session['cat_selected'] = int(cat)

        main = self.main_ui()

        return main.render()

    @url('^/handle/.+')
    def handle_generic(self, req, start_response):
        # Iterate through the IEventDispatchers and find someone who will take care of the event
        # TODO: use regexp for shorter event names, ex. 'btn_clickme/click'
        path = req['PATH_INFO'].split('/')
        event = '/'.join(path[2:4])
        params = path[4:]
        handler = None

        # Current module
        cat = self.app.session.get('cat_selected',0)

        if self.categories[cat].match_event(event):
            vars = get_environment_vars(req)
            result = self.categories[cat].event(event, params, vars = vars)
            if result is not None:
                # Usefull for inplace AJAX calls (that returns partial page)
                return result.render()

        # We have no result or handler - return default page
        main = self.main_ui()

        return main.render()

