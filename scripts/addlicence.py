#!/usr/bin/env python

import os.path
import tempfile
import shutil
import argparse
import contextlib

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

    # #------------------------------------------------------------------------------
    # def build(self, commentchar, border='-'*79, sectionbreak='{:^80}'.format('- - -')):

    #     headerlines = [border]

    #     for e in ['', self.copyright, '', self.body, '', sectionbreak, '', self.addon, '']:
    #         for line in e.split('\n'):
    #             headerlines += [line]
    #     headerlines += [border]

    #     return '\n'.join([ commentchar+l for l in headerlines])
    # #------------------------------------------------------------------------------

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
    '.tcl':'#',
    '.c': '//',
    '.vhd': '--',
    '.dep': '#',
    '.sh': '#',
    '.v': '//',
    }


#------------------------------------------------------------------------------
def addlicence(rootDir, selection, dryrun):

    # rootDir = '.'
    extensions = {}
    licHeader = ApacheHeader()

    for ext in selection:
        if ext not in licensable:
            print "Error: unknown extension", ext
            raise SystemExit(1)

    for dirName, subdirList, fileList in os.walk(rootDir):
        if dirName.startswith(os.path.join(rootDir,'.')):
            continue

        print('Inspecting directory: %s' % dirName)

        for fname in fileList:
            root, ext = os.path.splitext(fname)
            extensions.setdefault(ext, []).append(os.path.join(dirName,fname))
            print('\t%s' % fname)

    print 'File extensions found:', extensions.keys()
    print
    for ext in selection:
        if ext not in extensions:
            print '> No files with extension', ext, 'found in', rootDir
            continue
        print '---','Processing extension',ext,'---'
        # print extensions[ext]

        for filepath in extensions[ext]:
            print 'Processing', filepath
            print ' + Inspecting file...'
            if not check(filepath, licHeader):
                print 'Licence header detected, skipping...'
                continue
            print ' + Patching',filepath
            if dryrun:
                print "   - dry run mode: nothing done"
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
    print 'Temporary directory', tmpdir, 'created'
    tmpfilepath = os.path.join(tmpdir, os.path.basename(filepath))
    print tmpfilepath
    shutil.copy2(filepath, tmpfilepath)

    with contextlib.nested(open(filepath, 'w'), open(tmpfilepath, 'r')) as (A, B):

        # Start from the header
        A.write(header.build(licensable[ext]))

        # Add 2 blank lines
        A.write('\n\n')

        for line in B:
            A.write(line)

    shutil.rmtree(tmpdir)
    print 'Temporary directory', tmpdir, 'deleted'
#------------------------------------------------------------------------------

# Add comment character for file type
# 

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('folders', default=['.'],nargs='+')
    parser.add_argument('-n', dest='dryrun', default=False, action='store_true', help='Dry run, no chances will be applied')
    args = parser.parse_args()
    print args
    for folder in args.folders:
        addlicence(folder, ['.vhd', '.tcl', '.v', '.dep'], args.dryrun)

