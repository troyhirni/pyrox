
# pyrox

    
    Copyright 2015-2017 Troy Hirni
    This file is part of the pyrox project, distributed under
    the terms of the GNU Affero General Public License.
    
    The pyrox project is free software. You can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    


## about pyrox

The pyrox project contains experimental work. It's an attempt to find
the best organization of functions and classes in a library that can
be used in a variety of ways - as the foundation for applications,
for light, general use in the interpreter, or anything in between.

Package Goals:
 * rely only on built-in python modules and functions
 * work in both python 2 and 3
 * give special attention to unicode issues



** UPDATE **

Here's a major overhaul of pyrox, designed to help reduce the memory
requirements since the `hubcap` package (if I can ever work out the
bugs) will probably usually involve a lot of separate processess.


