import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.gen
import tornado.escape
import tornado.httpclient
import tornado.httputil
import tornado.process
import tornado.log
import tornado.websocket
import tornado.locks
import tornado.locale
import logging
import json
class MainHandler(tornado.web.RequestHandler):
    async def post(self):
        # TODO: upload twitter.com.har file and call dumper with it. then return to the user a zip file with the results
        pass


async def main():
    tornado.log.enable_pretty_logging()
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", MainHandler),
    ])
    server = tornado.httpserver.HTTPServer(app)
    logging.info("Listing on port 8888")
    server.listen(8888)
    await tornado.locks.Event().wait()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    tornado.ioloop.IOLoop.current().run_sync(main)