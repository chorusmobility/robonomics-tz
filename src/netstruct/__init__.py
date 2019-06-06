###############################################################################
#
# Copyright 2012 Stendec <me@stendec.me>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################
"""
This module performs conversions between Python values and packed binary data
suitable to be sent over a network connection. It functions in many ways
identically to the standard library module :module:`struct`. However, it uses
network byte order by default, and has support for variable-length strings.
"""

###############################################################################
# Imports
###############################################################################

from __future__ import unicode_literals

from struct import Struct as _Struct, error, calcsize as _calcsize


try:
    # Stupid Python 3...
    range = xrange
except NameError:
    pass

###############################################################################
# Exports and Constants
###############################################################################

__all__ = (
    "NetStruct",

    "pack", "unpack", "obj_unpack", "iter_unpack",
    "minimum_size", "initial_size"
)

__version_info__ = (1, 1, 1)
__version__ = ".".join(map(str, __version_info__))

bytes = type(b"")


###############################################################################
# Unpacker Class
###############################################################################

class Unpacker(object):
    """
    Instances of Unpacker are created when you call a NetStruct's
    :func:`~NetStruct.obj_unpack` method. These are used, as are the iterators
    returned by :func:`NetStruct.iter_unpack`, to unpack a NetStruct over
    time as you buffer more data. However, the Unpacker instance provides a
    nicer interface.

    .. code-block:: python

        >>> import netstruct
        >>> obj = netstruct.obj_unpack(b"ih$5b")
        >>> obj.remaining
        11
        >>> obj.feed(b"1234\x00\x0512345")
        5
        >>> obj.feed(b"\x00\x01\x02\x03\x04 so there")
        0
        >>> obj.result
        [825373492, b'12345', 0, 1, 2, 3, 4]
        >>> obj.unused_data
        b' so there'
    """

    __slots__ = ("_pairs", "_data", "_result", "_remaining")

    def __init__(self, netstruct, data=b""):
        self._pairs = netstruct._pairs[:]
        self._remaining = netstruct._minsize
        self._data = b""
        self._result = []

        if data:
            self.feed(data)

    def __repr__(self):
        if self.remaining:
            part = "remaining=%r" % self.remaining
        else:
            part = "result=%r, unused_data=%r" % (self.result, self.unused_data)

        return "<%s[%s] at 0x%08X>" % (
            self.__class__.__name__,
            part,
            id(self)
        )

    @property
    def remaining(self):
        """
        The number of remaining bytes needed to finish unpacking the data.
        """
        return max(0, self._remaining - len(self._data))

    @property
    def result(self):
        """ The resulting object, after all unpacking has completed. """
        return None if self._remaining else self._result

    @property
    def unused_data(self):
        """
        A string which contains any bytes that weren't used in the construction
        of the object.
        """
        return b"" if self._remaining else self._data

    ##### Methods #############################################################

    def feed(self, data):
        """
        Unpack *data* and return the number of remaining bytes needed to
        finish unpacking the NetStruct.
        """
        self._data += data

        while self._pairs:
            struct, count, has_string = self._pairs[0]

            if struct:
                needed = struct.size
                if needed > len(self._data):
                    return self._remaining - len(self._data)

                self._result.extend(struct.unpack(self._data[:needed]))
                self._data = self._data[needed:]
                self._remaining -= needed

                if has_string:
                    self._pairs[0] = None, count, has_string
                    self._remaining += self._result[-1]

            if has_string:
                needed = self._result[-1]
                if needed > len(self._data):
                    return self._remaining - len(self._data)

                self._result.pop()
                self._result.append(self._data[:needed])
                self._data = self._data[needed:]
                self._remaining -= needed

            self._pairs.pop(0)

        return 0

    send = feed


###############################################################################
# NetStruct Class
###############################################################################

class NetStruct(object):
    """
    Return a new NetStruct object which writes and reads binary data according
    to the format string *format*. It's more efficient, as it is with
    :class:`struct.Struct`, to create a NetStruct object once and call its
    methods rather than calling the :module:`netstruct` functions with the
    same format, as the format only has to be compiled once.

    The NetStruct object works as similarly to :class:`struct.Struct` as is
    possible, with two differences.

    When using a NetStruct, the byte order defaults to network byte order
    (big-endian). This ensures, among other things, that the generated strings
    won't have any padding bytes.

    Additionally, the NetStruct supports the formatting character ``$``, which
    signifies a variable-length string. When the ``$`` is encountered during
    unpacking, the most recently unpacked value will be used as the string's
    length. Attempting to unpack a non-numeric value, such as ``?`` (bool),
    will raise a :class:`struct.error`. As an example of unpacking::

        >>> netstruct.unpack(b"b$", b"\x0cHello World!")
        [b'Hello World!']

    When the ``$`` is encountered during packing, the string length will be
    used for the value directly before the string. Example::

        >>> netstruct.pack(b"b$", b"Hello World!")
        b'\x0cHello World!'
    """

    __slots__ = ("_format", "_pairs", "_minsize", "_initsize", "_count")

    def __init__(self, format):
        self._format = format
        self._minsize = 0
        self._count = 0

        if not format:
            self._pairs = []
            self._initsize = 0
        elif not isinstance(format, bytes):
            raise TypeError("NetStruct() format must be a byte string.")
        else:
            # Make sure there aren't any back-to-back strings and/or arrays.
            if b"$$" in format:
                raise error("invalid sequence in netstruct format")

            # Break the format down.
            self._pairs = pairs = []

            if format[:1] in b"@=<>!":
                byte_order = format[:1]
                format = format[1:]
            else:
                byte_order = b"!"

            while format:
                segment, sep, format = format.partition(b"$")

                if sep and (not segment or not segment[-1:] in b"bBhHiIlLqQP"):
                    raise error("bad char in struct format")

                st = _Struct(byte_order + segment)
                self._minsize += st.size
                count = _count(segment)
                self._count += count
                pairs.append((st, count, sep))

            self._initsize = pairs[0][0].size

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self._format)

    @property
    def count(self):
        """ The number of variables represented by this NetStruct. """
        return self._count

    @property
    def format(self):
        """ The format string used to construct this NetStruct. """
        return self._format

    @property
    def minimum_size(self):
        """ The minimum possible size of this NetStruct. """
        return self._minsize

    @property
    def initial_size(self):
        """
        The size of this NetStruct up to the first variable-length string.
        """
        return self._initsize

    ##### Methods #############################################################

    def pack(self, *data):
        """
        Return a string containing the values *data packed according to this
        NetStruct's format.
        """
        result = []
        append = result.append

        if len(data) != self._count:
            raise error("pack requires exactly %d arguments", self._count)

        for struct, count, has_string in self._pairs:
            if has_string:
                append(struct.pack(*data[:count-1] +
                                           (len(data[count-1]),)))
                append(data[count-1])
            else:
                append(struct.pack(*data[:count]))
            data = data[count:]

        return b"".join(result)

    def unpack(self, data):
        """
        Unpack a string of data according to this NetStruct's format. Raises
        a :class:`struct.error` if there isn't enough data provided.
        """
        out = next(self.iter_unpack(data))
        if isinstance(out, int):
            raise error("unpack requires a string argument of length %d" % (len(data) + out))
        return out

    def obj_unpack(self, data=b""):
        """
        Use an :class:`Unpacker` instance to unpack a string of data
        using this NetStruct's format.

        See :class:`Unpacker` for more details.
        """
        return Unpacker(self, data)

    def iter_unpack(self, data=b""):
        """
        Unpack a string of data according to this NetStruct's format.

        Because the length of the string needed to unpack a NetStruct with a
        variable length string is unknown, this method returns an iterator,
        able to request additional data until it is able to unpack the entire
        message.

        When using the iterator, calls to next(it) and it.send() will return
        either the number of bytes needed to finish unpacking, or a list with
        the completed value. As such, the following is an example of how you
        might use this::

            >>> ns = NetStruct(b"ih$5b")
            >>> it = ns.iter_unpack()
            >>> next(it)
            11
            >>> it.send(b"\x00\x00\x05\x12\x00\x0b")
            16
            >>> it.send(b"largeBiomes")
            5
            >>> it.send(b"\x00\x00\x01\x00\x08")
            [1298, b'largeBiomes', 0, 0, 1, 0, 8]

        You may also provide an initial string to start the process. Be aware
        that, if you provide a long enough string, the first call to next(it) or
        .send(it) may return the completed value.

        Once the completed value is returned, you may make one last call to
        next(it) or .send(it) to retrieve any unconsumed data.
        """
        result = []
        remaining = self._minsize

        for struct, count, has_string in self._pairs:

            needed = struct.size
            while needed > len(data):
                new_data = yield remaining - len(data)
                if new_data:
                    data += new_data

            result.extend(struct.unpack(data[:needed]))
            data = data[needed:]
            remaining -= needed

            if has_string:
                needed = result.pop()
                while needed > len(data):
                    new_data = yield (remaining + needed) - len(data)
                    if new_data:
                        data += new_data

                result.append(data[:needed])
                data = data[needed:]

        yield result
        yield data

###############################################################################
# Private Methods
###############################################################################

def _count(format):
    """
    Count the number of variables needed to pack a given format.
    """
    if format[:1] in b"@=<>!":
        format = format[1:]

    count = 0
    q = b""

    for index in range(len(format)):
        char = format[index:index+1]
        if char.isdigit():
            q += char
            continue
        elif char in b" \t\r\n":
            if q:
                raise error("bad char in struct format")
            continue
        elif char in b"ps":
            count += 1
            q = b""
        elif char in b"xcbB?hHiIlLqQfdP":
            count += int(q or 1)
            q = b""
        else:
            raise error("bad char in struct format")

    return count


###############################################################################
# Public Methods
###############################################################################

def pack(format, *data):
    """
    Return a string containing the values *data packed according to the
    given format.
    """
    return NetStruct(format).pack(*data)

def unpack(format, data):
    """
    Unpack a string of data that has been packed according to the given format.
    """
    return NetStruct(format).unpack(data)

def iter_unpack(format, initial=b""):
    """
    Use an iterator to unpack a string of data that has been packed according
    to the given format. See :meth:`NetStruct.iter_unpack` for more details.
    """
    return NetStruct(format).iter_unpack(initial)

def obj_unpack(format, initial=b""):
    """
    Use an :class:`Unpacker` to unpack a string of data that has been packed
    according to the given format. See :class:`Unpacker` for more details.
    """
    return NetStruct(format).obj_unpack(initial)

def minimum_size(format):
    """
    Return the minimum possible size of the given packed data format.
    """
    if not format[:1] in b"@=<>!":
        format = b"!" + format

    return _calcsize(format.replace(b"$", b""))

def initial_size(format):
    """
    Return the size of the given packed data format up to the first
    variable-length string.
    """
    if format[:1] in b"@=<>!":
        byte_order = format[:1]
        format = format[1:]
    else:
        byte_order = b"!"

    index = format.find(b"$")
    if not index:
        return 0
    elif index > 0:
        if b"$$" in format:
            raise error("invalid sequence in netstruct format")
        format = format[:index]
    return _calcsize(byte_order + format)
