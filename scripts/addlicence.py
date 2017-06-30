#!/usr/bin/env python

import os.path
import tempfile
import shutil
import argparse
import contextlib
import logging
import coloredlogs

class ApacheHeader(object):
    """docstring for ApacheHeader"""

    _copyright='''
   Copyright 2017 - Rutherford Appleton Laboratory and University of Bristol
'''

    _body='''
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
    _addon='''
   Additional information about ipbus-firmare and the list of ipbus-firmware
   contacts are available at

       https://ipbus.web.cern.ch/ipbus
'''

    def __init__(self):
        super(ApacheHeader, self).__init__()

    @property
    def copyright(self):
        return self._copyright.strip('\n')

    @property
    def body(self):
        return self._body.strip('\n')

    @property
    def addon(self):
        return self._addon.strip('\n')

    #------------------------------------------------------------------------------
    def build(self, commentchar='', border='-'*79, sectionbreak='{:^80}'.format('- - -').rstrip()):

        rawtext = '\n\n'.join([border, self.copyright, self.body, sectionbreak, self.addon, border])

        text = ''
        for line in rawtext.split('\n'):
            text += commentchar+line+'\n'

        return text
    #------------------------------------------------------------------------------

    def __len__(self):
        return self.build().count('\n')

licensable = {
    '.tcl': ('#', None, None),
    '.c':   ('//', None, None),
    '.vhd': ('--', None, None),
    '.dep': ('#', None, None),
    '.sh':  ('#', None, None),
    '.v':   ('//', None, None),
    '.xml': ('', '<!--', '-->'),
    '.ucf': ('#', None, None),
    }


#------------------------------------------------------------------------------
def addlicence(rootDir, selection, dryrun):

    # rootDir = '.'
    extensions = {}
    licHeader = ApacheHeader()

    for ext in selection:
        if ext not in licensable:
            logging.error("Error: unknown extension %s", ext)
            raise SystemExit(1)

    logging.info('Searching for files and folders')
    for dirName, subdirList, fileList in os.walk(rootDir):
        if dirName.startswith(os.path.join(rootDir,'.')):
            continue

        logging.debug('Inspecting directory: %s', dirName)

        for fname in fileList:
            root, ext = os.path.splitext(fname)
            extensions.setdefault(ext, []).append(os.path.join(dirName,fname))
            logging.debug('   %s', fname)

    logging.info('File extensions found: %s', extensions.keys())
    for ext in selection:
        if ext not in extensions:
            logging.warn('No files with extension %s found in %s', ext, rootDir)
            continue
        logging.info('--- Processing extension %s ---', ext)
        # print extensions[ext]

        for filepath in extensions[ext]:
            logging.info("Processing %s", filepath)
            logging.info(" + Inspecting file...")
            if not check(filepath, licHeader):
                logging.warning(" + Licence header detected, skipping...")
                continue
            logging.info(" + Patching %s",filepath)
            if dryrun:
                logging.warn("   - dry run mode: nothing done")
                continue
            prepend(filepath, ext, licHeader)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def check(filepath, header):
    """
    Check whether the header is already included in the file by looking for the 
    copyright line in the first lines of the file
    """

    # print header.copyright
    with open(filepath, 'r') as A:
        for _ in xrange(len(header)):
            # Read one line
            line = A.readline()
            # Search for the copyright 
            idx = line.find(header.copyright.strip())
            # Stop here if found
            if idx != -1:
                return False
        return True
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def prepend(filepath, ext, header):

    tmpdir = tempfile.mkdtemp()
    logging.debug('Temporary directory %s created', tmpdir)
    tmpfilepath = os.path.join(tmpdir, os.path.basename(filepath))
    logging.debug('Original file copied to %s', tmpfilepath)
    shutil.copy2(filepath, tmpfilepath)

    with contextlib.nested(open(filepath, 'w'), open(tmpfilepath, 'r')) as (A, B):

        # Work around shebangs
        firstline = B.readline()
        if firstline.startswith('#!'):
            A.write(firstline)
        else:
            B.seek(0)

        comment, pre, post = licensable[ext]

        if pre is not None:
            A.write(pre+'\n')

        # Start from the header
        A.write(header.build(comment))

        if post is not None:
            A.write(post+'\n')

        # Add 2 blank lines
        A.write('\n\n')

        for line in B:
            A.write(line)

    shutil.rmtree(tmpdir)
    logging.debug('Temporary directory deleted %s', tmpdir)
#------------------------------------------------------------------------------

# custom class to validate 'exec' variables
class SplitAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        values = [ (v if v[0] == '.' else '.'+v) for v in values.split(',') ]

        setattr(namespace, self.dest, values)



if __name__ == '__main__':

    coloredlogs.install(level='DEBUG',
                        # fmt='%(asctime)s %(levelname)-8s: %(message)s',
                        fmt='%(levelname)-8s: %(message)s',
                        field_styles={'asctime': {'color': 'blue'}}
                        )

    parser = argparse.ArgumentParser()
    parser.add_argument('folders', default=['.'],nargs='+')
    parser.add_argument('-n', dest='dryrun', default=False, action='store_true', help='Dry run, no chances will be applied')
    parser.add_argument('-e', dest='extensions', default=['.vhd', '.tcl', '.v', '.dep', '.sh'], action=SplitAction, help='Extensions to processed')
    args = parser.parse_args()

    # extensions =  ['.vhd', '.tcl', '.v', '.dep', '.sh']
    logging.info('Apache licence header will be applied to the following extensions'+' '.join(args.extensions))

    for folder in args.folders:
        addlicence(folder, args.extensions, args.dryrun)

