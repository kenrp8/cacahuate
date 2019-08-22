from unittest.mock import MagicMock
import simplejson as json

from cacahuate.handler import Handler
from cacahuate.models import Execution, Pointer
from cacahuate.node import Form
from cacahuate.xml import Xml

from ..utils import make_pointer, make_user


def test_true_condition_node(config, mongo):
    ''' conditional node will be executed if its condition is true '''
    # test setup
    handler = Handler(config)
    user = make_user('juan', 'Juan')
    ptr = make_pointer('condition.2018-05-17.xml', 'start_node')
    channel = MagicMock()

    mongo[config["EXECUTION_COLLECTION"]].insert_one({
        '_type': 'execution',
        'id': ptr.proxy.execution.get().id,
        'state': Xml.load(config, 'condition').get_state(),
    })

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('mistery', [
            {
                'name': 'password',
                'type': 'text',
                'value': 'abrete sésamo',
            },
        ])],
    }, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'condition1'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('condition1', [
            {
                'name': 'condition',
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': True,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'mistical_node'


def test_false_condition_node(config, mongo):
    ''' conditional node won't be executed if its condition is false '''
    # test setup
    handler = Handler(config)
    user = make_user('juan', 'Juan')
    ptr = make_pointer('condition.2018-05-17.xml', 'start_node')
    channel = MagicMock()

    mongo[config["EXECUTION_COLLECTION"]].insert_one({
        '_type': 'execution',
        'id': ptr.proxy.execution.get().id,
        'state': Xml.load(config, 'condition').get_state(),
    })

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('mistery', [
            {
                'name': 'password',
                'type': 'text',
                'value': '123456',
            },
        ])],
    }, channel)

    # assertions
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'condition1'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('condition1', [
            {
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': False,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'condition2'


def test_anidated_conditions(config, mongo):
    ''' conditional node won't be executed if its condition is false '''
    # test setup
    handler = Handler(config)
    user = make_user('juan', 'Juan')
    ptr = make_pointer('anidated-conditions.2018-05-17.xml', 'a')
    channel = MagicMock()

    mongo[config["EXECUTION_COLLECTION"]].insert_one({
        '_type': 'execution',
        'id': ptr.proxy.execution.get().id,
        'state': Xml.load(config, 'anidated-conditions').get_state(),
    })

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('a', [
            {
                'name': 'a',
                'value': '1',
            },
        ])],
    }, channel)

    # assertions
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'outer'

    # rabbit called
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('outer', [
            {
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': True,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    handler.call(rabbit_call, channel)

    # assertions
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'b'

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('b', [
            {
                'name': 'b',
                'value': '-1',
            },
        ])],
    }, channel)

    # assertions
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'inner1'

    # rabbit called
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('inner1', [
            {
                'name': 'condition',
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': False,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    handler.call(rabbit_call, channel)

    # assertions
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'f'

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('f', [
            {
                'name': 'f',
                'value': '-1',
            },
        ])],
    }, channel)

    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'g'


def test_ifelifelse_if(config, mongo):
    ''' else will be executed if preceding condition is false'''
    # test setup
    handler = Handler(config)
    user = make_user('juan', 'Juan')
    ptr = make_pointer('else.2018-07-10.xml', 'start_node')
    channel = MagicMock()

    mongo[config["EXECUTION_COLLECTION"]].insert_one({
        '_type': 'execution',
        'id': ptr.proxy.execution.get().id,
        'state': Xml.load(config, 'else').get_state(),
    })

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('secret01', [
            {
                'name': 'password',
                'type': 'text',
                'value': 'incorrect!',
            },
        ])],
    }, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'condition01'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('condition01', [
            {
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': True,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    channel = MagicMock()
    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'action01'

    # rabbit called to notify the user
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    assert args['exchange'] == 'charpe_notify'

    channel = MagicMock()
    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('form01', [
            {
                'name': 'answer',
                'value': 'answer',
            },
        ])],
    }, channel)

    # execution finished
    assert len(Pointer.get_all()) == 0
    assert len(Execution.get_all()) == 0


def test_ifelifelse_elif(config, mongo):
    ''' else will be executed if preceding condition is false'''
    # test setup
    handler = Handler(config)
    user = make_user('juan', 'Juan')
    ptr = make_pointer('else.2018-07-10.xml', 'start_node')
    channel = MagicMock()

    mongo[config["EXECUTION_COLLECTION"]].insert_one({
        '_type': 'execution',
        'id': ptr.proxy.execution.get().id,
        'state': Xml.load(config, 'else').get_state(),
    })

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('secret01', [
            {
                'name': 'password',
                'type': 'text',
                'value': 'hocus pocus',
            },
        ])],
    }, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'condition01'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('condition01', [
            {
                'name': 'condition',
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': False,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    channel = MagicMock()
    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'elif01'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('elif01', [
            {
                'name': 'condition',
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': True,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    channel = MagicMock()
    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'action02'

    # rabbit called to notify the user
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    assert args['exchange'] == 'charpe_notify'

    channel = MagicMock()
    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('form01', [
            {
                'name': 'answer',
                'value': 'answer',
            },
        ])],
    }, channel)

    # execution finished
    assert len(Pointer.get_all()) == 0
    assert len(Execution.get_all()) == 0


def test_ifelifelse_else(config, mongo):
    ''' else will be executed if preceding condition is false'''
    # test setup
    handler = Handler(config)
    user = make_user('juan', 'Juan')
    ptr = make_pointer('else.2018-07-10.xml', 'start_node')
    channel = MagicMock()

    mongo[config["EXECUTION_COLLECTION"]].insert_one({
        '_type': 'execution',
        'id': ptr.proxy.execution.get().id,
        'state': Xml.load(config, 'else').get_state(),
    })

    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('secret01', [
            {
                'name': 'password',
                'type': 'text',
                'value': 'cuca',
            },
        ])],
    }, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'condition01'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('condition01', [
            {
                'name': 'condition',
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': False,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    channel = MagicMock()
    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'elif01'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('elif01', [
            {
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': False,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    channel = MagicMock()
    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'else01'

    # rabbit called
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    rabbit_call = {
        'command': 'step',
        'pointer_id': ptr.id,
        'input': [Form.state_json('else01', [
            {
                'name': 'condition',
                'state': 'valid',
                'type': 'bool',
                'value': True,
            },
        ])],
        'user_identifier': '__system__',
    }
    assert json.loads(args['body']) == rabbit_call

    channel = MagicMock()
    handler.call(rabbit_call, channel)

    # pointer moved
    assert Pointer.get(ptr.id) is None
    ptr = Pointer.get_all()[0]
    assert ptr.node_id == 'action03'

    # rabbit called to notify the user
    channel.basic_publish.assert_called_once()
    args = channel.basic_publish.call_args[1]
    assert args['exchange'] == 'charpe_notify'

    channel = MagicMock()
    handler.call({
        'command': 'step',
        'pointer_id': ptr.id,
        'user_identifier': user.identifier,
        'input': [Form.state_json('form01', [
            {
                'name': 'answer',
                'value': 'answer',
            },
        ])],
    }, channel)

    # execution finished
    assert len(Pointer.get_all()) == 0
    assert len(Execution.get_all()) == 0
