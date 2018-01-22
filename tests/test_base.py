# tests.test_base
# Test base collection and resource classes
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Fri Jan 19 11:19:12 2018 -0500
#
# ID: test_base.py [] benjamin@bengfort.com $

"""
Test base collection and resource classes
"""

##########################################################################
## Imports
##########################################################################

import pytest

from geonet.base import *
from contextlib import contextmanager
from geonet.exceptions import ValidationError


##########################################################################
## Fixtures
##########################################################################

class MockResource(Resource):

    REQUIRED_KEYS = ('foo', 'bar')
    EXTRA_KEYS = ('baz', 'zab')
    EXTRA_DEFAULT = 42

    def __str__(self):
        return "{foo:} {bar:}".format(**self)


class MockCollection(Collection):

    RESOURCE = MockResource


##########################################################################
## Helper Functions
##########################################################################

@contextmanager
def isvalid():
    try:
        yield
    except ValidationError as e:
        pytest.fail(str(e))



##########################################################################
## Test Cases
##########################################################################

class TestResource(object):
    """
    Resource object should
    """

    def test_validation_not_required(self):
        """
        validate when no keys are required
        """

        with isvalid():
            Resource({})

    def test_validation_required(self):
        """
        validate when keys are required
        """
        with pytest.raises(ValidationError):
            MockResource({})

        with isvalid():
            MockResource({'foo': 42, 'bar': 'red'})

    def test_validation_no_extra_keys(self):
        """
        validate when no extra keys need be added
        """
        resource = Resource({'extra': 'foo'})
        assert 'extra' in resource.data

    def test_validation_add_extra_defaults(self):
        """
        validate adds default extra keys
        """
        resource = MockResource({'foo': 42, 'bar': 'red'})
        for key in MockResource.EXTRA_KEYS:
            assert key in resource.data
            assert resource.data[key] == MockResource.EXTRA_DEFAULT

    def test_get_item(self):
        """
        get an item from the data by key
        """
        resource = MockResource({'foo': 42, 'bar': 'red'})
        assert resource['foo'] == 42
        assert resource['bar'] == 'red'

    def test_set_item(self):
        """
        set an item into the data by key
        """
        resource = MockResource({'foo': 42, 'bar': 'red'})
        assert resource['foo'] == 42
        resource['foo'] = 36
        assert resource['foo'] == 36

    def test_del_item(self):
        """
        delete an item from the data
        """
        resource = MockResource({'foo': 42, 'bar': 'red'})
        del resource['foo']
        assert 'foo' not in resource.data

    def test_contains(self):
        """
        contain an item
        """
        resource = MockResource({'foo': 42, 'bar': 'red', 'extra': '**'})
        assert 'foo' in resource
        assert 'bar' in resource
        assert 'extra' in resource
        assert 'baz' in resource
        assert 'zab' in resource

    def test_len(self):
        """
        return the length of the resource
        """
        resource = MockResource({'foo': 42, 'bar': 'red', 'extra': '**'})
        assert len(resource) == 5

    def test_iter(self):
        """
        test iteration over keys in resource
        """
        expected = {'foo', 'bar', 'extra', 'baz', 'zab'}
        resource = MockResource({'foo': 42, 'bar': 'red', 'extra': '**'})
        for key in resource:
            assert key in expected

    def test_items(self):
        """
        test iteration over key value pairs in resource
        """
        resource = MockResource({'foo': 42, 'bar': 'red', 'extra': '**'})
        for key, val in resource.items():
            assert key in resource
            assert resource[key] == val

    def test_values(self):
        """
        test iteration over values in resource
        """
        expected = {42, 'red', '**'}
        resource = MockResource({'foo': 42, 'bar': 'red', 'extra': '**'})
        for val in resource.values():
            assert val in expected

    def test_get(self):
        """
        test ability to get an item from data
        """
        resource = MockResource({'foo': 42, 'bar': 'red', 'extra': '**'})
        assert resource.get('foo', 100) == 42
        assert resource.get('food', 100) == 100


class TestCollection(object):
    """
    Collection object should
    """

    def test_creates_items(self):
        """
        create and iterate over resources from data on init
        """

        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ])

        for item in collection:
            assert isinstance(item, MockResource)

        assert len(collection) == 2

    def test_creates_item_with_region(self):
        """
        creates resources with region data
        """

        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ], 'us-east-1')

        for item in collection:
            assert hasattr(item, 'region')
            assert item.region == 'us-east-1'

    def test_contains_item(self):
        """
        test the ability to check if an item is contained
        """

        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ])

        # Test by index
        assert MockResource({'foo': 23, 'bar': 'blue'}) in collection
        assert MockResource({'foo': 18, 'bar': 'green'}) in collection
        assert MockResource({'foo': 78, 'bar': 'pink'}) not in collection

    def test_getitem(self):
        """
        test ability to get an item by index or string
        """
        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ])

        # By index
        assert collection[0] == MockResource({'foo': 23, 'bar': 'blue'})
        assert collection[1] == MockResource({'foo': 18, 'bar': 'green'})

        with pytest.raises(IndexError):
            collection[2]

        # By string
        assert collection['23 blue'] == MockResource({'foo': 23, 'bar': 'blue'})
        assert collection['18 green'] == MockResource({'foo': 18, 'bar': 'green'})

        with pytest.raises(KeyError):
            collection['78 pink']

    def test_setitem(self):
        """
        test ability to set an item by index
        """
        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ], 'us-east-2')

        collection[1] = {'foo': 27, 'bar': 'purple'}
        assert collection[1] == MockResource({'foo': 27, 'bar': 'purple'})
        assert collection[1].region == collection.region

    def test_delitem(self):
        """
        test ability to delete an item by index
        """
        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ], 'us-east-2')

        del collection[1]
        assert len(collection) == 1
        assert str(collection[-1]) == '23 blue'

    def test_append(self):
        """
        test ability to append an item to the collection
        """
        collection = MockCollection([
            {'foo': 23, 'bar': 'blue'},
            {'foo': 18, 'bar': 'green'},
        ], region='us-west-2')

        collection.append({'foo': 27, 'bar': 'purple'})
        assert collection[-1] == MockResource({'foo': 27, 'bar': 'purple'})
        assert collection[-1].region == collection.region

    def test_extend_collection(self):
        """
        test ability to extend a collection with another collection
        """

        alpha = MockCollection([
            {'foo': 1, 'bar': 'blue'},
            {'foo': 2, 'bar': 'green'},
        ], region='us-west-2')

        bravo = MockCollection([
            {'foo': 3, 'bar': 'pink'},
            {'foo': 4, 'bar': 'gold'},
        ], region='us-east-1')

        alpha.extend(bravo)
        assert len(alpha) == 4
        assert len(bravo) == 2

        assert str(alpha[0]) == '1 blue'
        assert alpha[0].region == 'us-west-2'
        assert str(alpha[1]) == '2 green'
        assert alpha[1].region == 'us-west-2'
        assert str(alpha[2]) == '3 pink'
        assert alpha[2].region == 'us-east-1'
        assert str(alpha[3]) == '4 gold'
        assert alpha[3].region == 'us-east-1'

    def test_iadd_collection(self):
        """
        test ability to in place add a collection with another collection
        """

        alpha = MockCollection([
            {'foo': 1, 'bar': 'blue'},
            {'foo': 2, 'bar': 'green'},
        ], region='us-west-2')

        bravo = MockCollection([
            {'foo': 3, 'bar': 'pink'},
            {'foo': 4, 'bar': 'gold'},
        ], region='us-east-1')

        alpha += bravo
        assert len(alpha) == 4
        assert len(bravo) == 2

        assert str(alpha[0]) == '1 blue'
        assert alpha[0].region == 'us-west-2'
        assert str(alpha[1]) == '2 green'
        assert alpha[1].region == 'us-west-2'
        assert str(alpha[2]) == '3 pink'
        assert alpha[2].region == 'us-east-1'
        assert str(alpha[3]) == '4 gold'
        assert alpha[3].region == 'us-east-1'

    def test_extend_collection_list(self):
        """
        test ability to extend a collection with another list
        """

        alpha = MockCollection([
            {'foo': 1, 'bar': 'blue'},
            {'foo': 2, 'bar': 'green'},
        ], region='us-west-2')

        bravo = [
            {'foo': 3, 'bar': 'pink'},
            {'foo': 4, 'bar': 'gold'},
        ]

        alpha.extend(bravo)
        assert len(alpha) == 4
        assert len(bravo) == 2

        assert str(alpha[0]) == '1 blue'
        assert alpha[0].region == 'us-west-2'
        assert str(alpha[1]) == '2 green'
        assert alpha[1].region == 'us-west-2'
        assert str(alpha[2]) == '3 pink'
        assert alpha[2].region == 'us-west-2'
        assert str(alpha[3]) == '4 gold'
        assert alpha[3].region == 'us-west-2'

    def test_iadd_collection_list(self):
        """
        test ability to in place add a collection with another list
        """

        alpha = MockCollection([
            {'foo': 1, 'bar': 'blue'},
            {'foo': 2, 'bar': 'green'},
        ], region='us-west-2')

        bravo = [
            {'foo': 3, 'bar': 'pink'},
            {'foo': 4, 'bar': 'gold'},
        ]

        alpha += bravo
        assert len(alpha) == 4
        assert len(bravo) == 2

        assert str(alpha[0]) == '1 blue'
        assert alpha[0].region == 'us-west-2'
        assert str(alpha[1]) == '2 green'
        assert alpha[1].region == 'us-west-2'
        assert str(alpha[2]) == '3 pink'
        assert alpha[2].region == 'us-west-2'
        assert str(alpha[3]) == '4 gold'
        assert alpha[3].region == 'us-west-2'
